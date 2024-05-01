from sklearn import preprocessing
import pandas as pd


def preprocess_data(data):
    label_encoder = preprocessing.LabelEncoder()
    indexes = [i for i in data.columns if data[i].dtype == 'object']
    for i in indexes:
        data[i] = label_encoder.fit_transform(data[i])
    columns = pd.read_csv("my_app/xgb_models/column_names.csv").values.flatten()
    data = data[columns]
    data = data.iloc[:, :]
    return data
