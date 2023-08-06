import pandas as pd
from sklearn import datasets
from tidyframe import nest, unnest

iris = datasets.load_iris()
df = pd.DataFrame(iris['data'], columns=iris.feature_names)
df['target'] = iris.target
df['target2'] = list(map(lambda x: str(x + 1), df.target))
columns = ['target', 'target2']
df2 = nest(df, columns, key='data_nest', copy=True)


def test_unnest_basic():
    unnest(df2)[df.columns]


def test_unnest_list():
    df_string = pd.DataFrame()
    df_string['a'] = list('11223')
    df_string['b'] = list('22334')
    df_string['c'] = ['a', 'bb', 'ccc', 'dddd', 'eeeee']
    df_string['d'] = df_string['c'].map(lambda x: list(x))
    unnest(df_string)


def test_unnest_split():
    df_comma = pd.DataFrame({'a': list('12'), "b": ['A,B,C', 'D,E,F,G']})
    df_comma['b_split'] = df_comma['b'].apply(lambda x: x.split(','))
    unnest(df_comma)


def test_deepcopy():
    unnest(df2, copy=True)


def test_unnest_list():
    df_string = pd.DataFrame()
    df_string['a'] = list('11223')
    df_string['b'] = list('22334')
    df_string['c'] = ['a', 'bb', 'ccc', 'dddd', 'eeeee']
    df_string['d'] = df_string['c'].map(lambda x: list(x))
    unnest(df_string, drop=['a'], copy=True)


def test_unnest_mulit_nest_dataframe():
    df2['data_nest2'] = df2['data_nest']
    unnest(df2)
