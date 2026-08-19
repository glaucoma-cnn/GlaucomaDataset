import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score



def load_data(csv_path):
    return pd.read_csv(csv_path)

def load_metadata(metadata_path):
    meta = pd.read_csv(metadata_path)
    meta = meta[['names', 'types']].rename(columns={'names': 'image_id', 'types': 'glaucoma_flag'})
    meta = meta[meta['glaucoma_flag'].isin([0, 1])]
    return meta


def merge_features_with_labels(features_df, metadata_df):
    return features_df.merge(metadata_df, on='image_id', how='inner')


def split_train_test(fileCSV):
    df_train = fileCSV[fileCSV['image_id'].str.contains('train')]
    df_test = fileCSV[~fileCSV['image_id'].str.contains('train')]
    return df_train, df_test

def evaluate_accuracy(df_test, result, target):
    y_test = df_test[target]
    y_pred = result['glaucoma_predicted']
    return accuracy_score(y_test, y_pred)


def train_model(df_train, features, target):
    X_train = df_train[features]
    y_train = df_train[target]

    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model


def predict(model, df_test, features):
    X_test = df_test[features]

    result = df_test[['image_id']].copy()
    result['glaucoma_predicted'] = model.predict(X_test)
    result['glaucoma_prob'] = model.predict_proba(X_test)[:, 1]
    return result


def save_result(df_result, output_folder, file_name):
    os.makedirs(output_folder, exist_ok=True)
    path = os.path.join(output_folder, file_name)
    df_result.to_csv(path, index=False)
    return path
