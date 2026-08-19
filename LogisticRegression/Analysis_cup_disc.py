import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
#from sklearn.metrics import accuracy_score


# aqui lê o csv que foi criado dentro do método analyze_optic_pairs() passando o endereço path da minha máquina 
def load_data(csv_path):
    return pd.read_csv(csv_path)

#Aqui lê o metadata.csv do dataset (que eu baixei localmente) e filtra somente as colunas {'names': 'image_id', 'types': 'glaucoma_flag'}
def load_metadata(metadata_path):
    meta = pd.read_csv(metadata_path)
    meta = meta[['names', 'types']].rename(columns={'names': 'image_id', 'types': 'glaucoma_flag'})
    meta = meta[meta['glaucoma_flag'].isin([0, 1])]
    return meta

#aqui estamos juntando as labels ("rotulos") com as features ("características") da imagem mantendo a união somente quando existir as mesmas imagens nos dois Dataframes
def merge_features_with_labels(features_df, metadata_df):
    return features_df.merge(metadata_df, on='image_id', how='inner')

#Aqui estamos dando um split em todas as imagens que possuem train E todas as imagens que NÃO possuem a palavra train no seu nome_id 
def split_train_test(fileCSV):
    df_train = fileCSV[fileCSV['image_id'].str.contains('train')]
    df_test = fileCSV[~fileCSV['image_id'].str.contains('train')]
    return df_train, df_test

# aqui estou criando o metodo para analisar a acurácia do logisticRegression pode descomentar para fins de teste
#def evaluate_accuracy(df_test, result, target):
   # y_test = df_test[target]
    #y_pred = result['glaucoma_predicted']
    #return accuracy_score(y_test, y_pred)


# aqui estamos treinando o modelo Logistic Regression - não coloquei a porcentagem de treino e teste porque o dataset já nos proporciona essa divisão
def train_model(df_train, features, target):
    X_train = df_train[features]
    y_train = df_train[target]

    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model


#aqui foi só um "fru-fru" para poder visualizar a predição que o nosso machine learning preveu para cada imagem entre 0 e 1
def predict(model, df_test, features):
    X_test = df_test[features]

    result = df_test[['image_id']].copy()
    result['glaucoma_predicted'] = model.predict(X_test)
    result['glaucoma_prob'] = model.predict_proba(X_test)[:, 1]
    return result

#aqui salva o resultado em um csv dentro de uma pasta que será criada (com o makedirs) com o nome results/
def save_result(df_result, output_folder, file_name):
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, file_name)
    df_result.to_csv(path, index=False)
    return path
