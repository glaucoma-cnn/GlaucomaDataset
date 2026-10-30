import os
import hashlib
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedGroupKFold

from config.Settings import (
    VALID_GLAUCOMA_LABELS,
    CROSS_VALIDATION_FOLDS,
    RANDOM_STATE,
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


# Preserva rótulos, origem, pacientes e nomes originais para os experimentos.
def load_metadata(metadata_path):
    try:
        meta = pd.read_csv(metadata_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Metadata do dataset não encontrado em '{metadata_path}'. "
            "Confira o caminho em main.py (baixado via kagglehub)."
        ) from e

    meta = meta[['names', 'types', 'patient_id', 'original_name', 'fundus']].copy()
    meta = meta.rename(columns={'names': 'image_id', 'types': 'glaucoma_flag'})
    meta['dataset'] = meta['image_id'].str.split('-').str[0]
    # Monta o caminho da fotografia dentro da pasta do dataset.
    dataset_folder = Path(metadata_path).parent
    meta['fundus_path'] = [
        dataset_folder / 'full-fundus' / str(name).lstrip('/')
        for name in meta['fundus']
    ]

    total = len(meta)
    meta = meta[meta['glaucoma_flag'].isin(VALID_GLAUCOMA_LABELS)]
    excluded = total - len(meta)
    if excluded:
        print(f"  {excluded} amostra(s) fora de {VALID_GLAUCOMA_LABELS} excluída(s) (ex.: suspeita de glaucoma).")

    return meta


# aqui estamos juntando as labels ("rotulos") com as features ("características") da imagem
# mantendo a união somente quando existir as mesmas imagens nos dois Dataframes
def merge_features_with_labels(features_df, metadata_df):
    return features_df.merge(metadata_df, on='image_id', how='inner', validate='one_to_one')


# aqui identificamos o paciente pelo metadata ou pelo nome original da CRFO
def get_patient_id(row):
    if pd.notna(row['patient_id']) and str(row['patient_id']).strip():
        return f"{row['dataset']}:{row['patient_id']}"

    if row['dataset'] == 'CRFO':
        # Os nomes dos dois olhos possuem a mesma parte antes de Left/Right Eye. (Regex)
        patient = re.fullmatch(r'(.+-P_\d+)-(?:Left|Right) Eye', str(row['original_name']))
        if not patient:
            raise ValueError(f"Paciente CRFO não reconhecido: {row['original_name']}")
        return f"CRFO:{patient[1]}"

    return None


# aqui comparamos os pixels da fotografia para identificar cópias exatas
def get_image_hash(image_path):
    with Image.open(image_path) as image:
        image = image.convert('RGB')
        pixels = str(image.size).encode() + image.tobytes()
        return hashlib.sha256(pixels).hexdigest()


# aqui colocamos pacientes, nomes repetidos e imagens idênticas no mesmo grupo
def create_groups(df):
    groups = list(range(len(df)))
    seen = {}

    for i, row in df.iterrows():
        original = None
        if pd.notna(row['original_name']) and str(row['original_name']).strip():
            original = f"{row['dataset']}:{str(row['original_name']).strip()}"

        identifiers = {
            'patient': row['patient_key'],
            'original': original,
            'image': row['image_hash'],
        }
        for kind, identifier in identifiers.items():
            if pd.isna(identifier):
                continue

            key = (kind, identifier)
            if key in seen:
                old_group = groups[i]
                same_group = groups[seen[key]]
                # Troca o grupo inteiro, incluindo imagens ligadas anteriormente.
                groups = [same_group if group == old_group else group for group in groups]
            else:
                seen[key] = i

    return [f'group_{group}' for group in groups]


# aqui preparamos os grupos que serão respeitados nos dois experimentos
def prepare_experiment_groups(df, output_folder='results'):
    df = df.reset_index(drop=True).copy()
    df['patient_key'] = df.apply(get_patient_id, axis=1)
    df['image_hash'] = df['fundus_path'].apply(get_image_hash)
    df['group_id'] = create_groups(df)

    columns = ['image_id', 'dataset', 'patient_key', 'image_hash', 'group_id']
    save_result(df[columns], output_folder, 'experiment_groups.csv')
    print(f"  {len(df)} imagens; {df['group_id'].nunique()} grupos; "
          f"{df['image_hash'].duplicated().sum()} cópias com pixels idênticos; "
          f"{df['patient_key'].isna().sum()} imagens sem paciente identificável.")
    return df


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


# experimento A: divide todas as imagens em cinco partes, respeitando os grupos
def cross_validate_model(df, features, target,
                         output_folder='results', file_name='cv_folds.csv'):
    cv = StratifiedGroupKFold(
        n_splits=CROSS_VALIDATION_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    splits = cv.split(df[features], df[target], groups=df['group_id'])
    return evaluate_folds(df, features, target, splits, output_folder, file_name)


# experimento B: deixa um dataset inteiro para teste em cada rodada
def leave_one_dataset_out(df, features, target,
                          output_folder='results', file_name='lodo_folds.csv'):
    df = df.reset_index(drop=True)
    datasets = sorted(df['dataset'].unique())
    if len(datasets) != 6:
        raise ValueError(f'LODO requer 6 datasets; encontrados: {datasets}')
    splits = []
    for dataset in datasets:
        test = df[df['dataset'] == dataset]
        train = df[df['dataset'] != dataset]
        # Retira do treino os grupos que aparecem no teste.
        train = train[~train['group_id'].isin(test['group_id'])]
        splits.append((train.index, test.index))
    return evaluate_folds(df, features, target, splits, output_folder, file_name)


# aqui treinamos e avaliamos o modelo em cada divisão dos experimentos
def evaluate_folds(df, features, target, splits, output_folder, file_name):
    rows = []
    assignments = []
    for fold, (idx_train, idx_val) in enumerate(splits, start=1):
        train, validation = df.iloc[idx_train], df.iloc[idx_val]
        if train.empty or validation.empty or train[target].nunique() < 2:
            raise ValueError(f'Fold {fold} vazio ou treino com apenas uma classe.')
        if set(train['group_id']) & set(validation['group_id']):
            raise ValueError(f'Vazamento de grupos no fold {fold}.')
        model = train_model(train, features, target)
        result = predict(model, validation, features)
        y_val = validation[target].to_numpy()
        y_pred = result['glaucoma_predicted'].to_numpy()

        rows.append({
            'fold': fold,
            'dataset_teste': '+'.join(sorted(validation['dataset'].unique())),
            'n_treino': len(idx_train),
            'n_validacao': len(idx_val),
            'n_excluidas_treino': len(df) - len(idx_train) - len(idx_val),
            'acertos': int((y_pred == y_val).sum()),
            'erros': int((y_pred != y_val).sum()),
            'acuracia': evaluate_accuracy(validation, result, target),
        })
        for role, subset in [('treino', train), ('teste', validation)]:
            assignments.append(subset[['image_id', 'dataset', 'group_id']].assign(fold=fold, papel=role))

    return save_fold_results(rows, assignments, features, output_folder, file_name)


# aqui salvamos as notas e as imagens de cada fold, junto com a média e o desvio
def save_fold_results(rows, assignments, features, output_folder, file_name):
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

    save_result(out, output_folder, file_name)
    fold_images = pd.concat(assignments, ignore_index=True)
    save_result(fold_images, output_folder, f'{Path(file_name).stem}_assignments.csv')

    print(f"  {Path(file_name).stem}: acurácia {mean:.2%} ± {std:.2%}")
    return mean, std
