import os
from datetime import datetime

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

from config.Settings import (
    VALID_GLAUCOMA_LABELS,
    CROSS_VALIDATION_FOLDS,
    RANDOM_STATE,
    GLAUCOMA_POSITIVE_LABEL,
    GLAUCOMA_NEGATIVE_LABEL,
)
# aqui lê o csv que foi criado dentro do método analyze_optic_pairs() passando o endereço path da minha máquina
def load_data(csv_path):
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"CSV de features não encontrado em '{csv_path}'. "
            "Rode analyze_optic_pairs() antes, ou confira o caminho em main.py."
        ) from e


# Aqui lê o metadata.csv do dataset (que eu baixei localmente) e filtra somente as colunas {'names': 'image_id', 'types': 'glaucoma_flag'}
def load_metadata(metadata_path):
    try:
        meta = pd.read_csv(metadata_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Metadata do dataset não encontrado em '{metadata_path}'. "
            "Confira o caminho em main.py (baixado via kagglehub)."
        ) from e

    meta = meta[['names', 'types']].rename(columns={'names': 'image_id', 'types': 'glaucoma_flag'})

    total = len(meta)
    meta = meta[meta['glaucoma_flag'].isin(VALID_GLAUCOMA_LABELS)]
    excluded = total - len(meta)
    if excluded:
        print(f"  {excluded} amostra(s) fora de {VALID_GLAUCOMA_LABELS} excluída(s) (ex.: suspeita de glaucoma).")

    return meta


# aqui estamos juntando as labels ("rotulos") com as features ("características") da imagem
# mantendo a união somente quando existir as mesmas imagens nos dois Dataframes
def merge_features_with_labels(features_df, metadata_df):
    return features_df.merge(metadata_df, on='image_id', how='inner')


# Aqui estamos dando um split em todas as imagens que possuem train E todas as imagens
# que NÃO possuem a palavra train no seu nome_id
def split_train_test(fileCSV):
    df_train = fileCSV[fileCSV['image_id'].str.contains('train')]
    df_test = fileCSV[~fileCSV['image_id'].str.contains('train')]

    if df_train.empty or df_test.empty:
        raise ValueError(
            "Split treino/teste vazio: confira se os image_id realmente contêm 'train' "
            "para as imagens de treino."
        )

    return df_train, df_test


# aqui estou criando o metodo para analisar a acurácia do logisticRegression pode descomentar para fins de teste
def evaluate_accuracy(df_test, result, target):
    y_test = df_test[target]
    y_pred = result['glaucoma_predicted']
    return accuracy_score(y_test, y_pred)


# aqui estamos treinando o modelo Logistic Regression - não coloquei a porcentagem de treino e teste porque o dataset já nos proporciona essa divisão
def train_model(df_train, features, target):
    X_train = df_train[features]
    y_train = df_train[target]

    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model


# aqui foi só um "fru-fru" para poder visualizar a predição que o nosso machine learning
# previu para cada imagem entre 0 e 1
def predict(model, df_test, features):
    X_test = df_test[features]

    result = df_test[['image_id']].copy()
    result['glaucoma_predicted'] = model.predict(X_test)
    result['glaucoma_prob'] = model.predict_proba(X_test)[:, 1]
    return result


# aqui salva o resultado em um csv dentro de uma pasta que será criada (com o makedirs) com o nome results/
def save_result(df_result, output_folder, file_name):
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, file_name)
    df_result.to_csv(path, index=False)
    return path

def cross_validate_model(df_train, features, target,
                         output_folder='results', file_name='cv_folds.csv'):
    X = df_train[features]
    y = df_train[target]
    cv = StratifiedKFold(n_splits=CROSS_VALIDATION_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    rows = []
    for fold, (idx_train, idx_val) in enumerate(cv.split(X, y), start=1):
        model = LogisticRegression()
        model.fit(X.iloc[idx_train], y.iloc[idx_train])

        y_val = y.iloc[idx_val]
        y_pred = model.predict(X.iloc[idx_val])

        rows.append({
            'fold': fold,
            'n_treino': len(idx_train),
            'n_validacao': len(idx_val),
            'acertos': int((y_pred == y_val).sum()),
            'erros': int((y_pred != y_val).sum()),
            'acuracia': accuracy_score(y_val, y_pred),
        })

    df_folds = pd.DataFrame(rows)
    mean = df_folds['acuracia'].mean()
    std = df_folds['acuracia'].std(ddof=0)

    summary = pd.DataFrame([
        {'fold': 'media', 'acuracia': mean},
        {'fold': 'desvio_padrao', 'acuracia': std},
    ])
    out = pd.concat([df_folds, summary], ignore_index=True).convert_dtypes()
    out['acuracia'] = out['acuracia'].round(4)
    out.insert(0, 'data_hora', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    out.insert(1, 'features', '+'.join(sorted(features)))

    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, file_name)
    out.to_csv(path, mode='a', header=not os.path.exists(path), index=False)

    print(f"  CV acurácia: {mean:.2%} ± {std:.2%}")
    return mean, std