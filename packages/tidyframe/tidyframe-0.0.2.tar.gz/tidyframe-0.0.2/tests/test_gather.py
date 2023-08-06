import pandas as pd
from sklearn import datasets
from tidyframe import gather

iris = datasets.load_iris()
df = pd.DataFrame(iris['data'], columns=iris.feature_names)
df['target'] = iris.target
df['target2'] = list(map(lambda x: 1 if x < 1 else 0, df.target))
col_gather = df.columns[:4]
df_short = df.head()


def test_gather_basic():
    gather(df_short[col_gather].reset_index().head(8), col_gather).head()


def test_gather_without_index():
    tmp = gather(df_short[col_gather])
    assert tmp.columns[0] == 'index'


def test_gather_assign_col():
    gather(df_short, col_gather)


def test_gather_str_key():
    gather(df_short, 'target')


def test_gather_with_index_name():
    df_short2 = df_short[col_gather]
    df_short2.index.name = 'index_with_name'
    assert gather(df_short2, col_gather).columns[0] == df_short2.index.name
