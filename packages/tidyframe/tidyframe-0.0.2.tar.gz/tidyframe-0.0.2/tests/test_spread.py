import pandas as pd
from sklearn import datasets
from tidyframe import gather, spread

iris = datasets.load_iris()
df = pd.DataFrame(iris['data'], columns=iris.feature_names)
df['target'] = iris.target
df['target2'] = list(map(lambda x: 1 if x < 1 else 0, df.target))
col_gather = df.columns[:4]
df_short = df.head()
df_short_gather = gather(df_short[col_gather])
df_short_gather2 = gather(df_short, col_gather)


def test_spread_basic():
    spread(df_short_gather, ['index'], 'key')


def test_spread_string():
    spread(df_short_gather, 'index', 'key')


def test_spread_mulit_value():
    df_short_gather2 = df_short_gather
    df_short_gather2['value2'] = df_short_gather2['value'] + 1
    spread(df_short_gather, 'index', 'key')


def test_spread_mulit_key():
    df_short_gather[
        'key_with_index'] = df_short_gather['key'] + "_" + df_short_gather['index'].astype(
            str)
    spread(df_short_gather, 'index', ['key', 'key_with_index'])


def test_spread_mulit_row_key():
    df_short_gather['index2'] = df_short_gather['index'] + 1
    spread(df_short_gather, ['index', 'index2'], 'key')
