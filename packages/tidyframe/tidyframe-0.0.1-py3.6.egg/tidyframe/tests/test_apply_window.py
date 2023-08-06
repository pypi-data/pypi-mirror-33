import pandas as pd
import numpy as np
from sklearn import datasets
from ..transform import nest, unnest, apply_window

iris = datasets.load_iris()
df = pd.DataFrame(iris['data'], columns=iris.feature_names)
df['target'] = iris.target
df['target2'] = list(map(lambda x: str(x +1),df.target))
field_apply = {k:v for (k, v) in (zip(df.columns[:2], [np.max, np.mean]))}
field_apply['sepal length (cm)'] = [np.min, np.max]
df_g = df.groupby('target')

def test_apply_window_basic():
    apply_window(df, np.mean, partition=['target'], columns=df.columns[1])

def test_apply_window_list_columns():
    apply_window(df, np.mean, partition=['target'], columns=df.columns[:3])

def test_apply_window_list_func():
    apply_window(df, field_apply, partition='target')

def test_apply_window_DataFrameGroupBy():
    apply_window(df.groupby('target'), field_apply).head()

def test_apply_window_all_list():
    apply_window(df_g, [np.mean, np.max], columns=['sepal length (cm)', 'sepal length (cm)'])

def test_apply_window_lsit_func_and_str_column():
    apply_window(df_g, [np.mean, np.max], columns='sepal length (cm)')



