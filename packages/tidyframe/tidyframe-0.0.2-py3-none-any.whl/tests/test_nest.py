import pandas as pd
from sklearn import datasets
from tidyframe import nest

iris = datasets.load_iris()
df = pd.DataFrame(iris['data'], columns=iris.feature_names)
df['target'] = iris.target
df['target2'] = list(map(lambda x: str(x + 1), df.target))
columns = df.columns[:4].tolist()


def test_nest_columns():
    nest(df, columns, key='data_nest', copy=True)


def test_nest_columns():
    nest(
        df, columns_minus=df.columns[4:6].tolist(), key='data_nest', copy=True)


def test_nest_group_by():
    nest(df.groupby(['target', 'target2']), key='data_nest', copy=True)


def test_nest_by_index():
    nest(df, df.columns[:4], key='data_nest', copy=True)


def test_nest_by_index_minus():
    nest(df, columns_minus=df.columns[4:6], key='data_nest', copy=True).head()


def test_nest_column_between():
    nest(
        df,
        columns_between=['sepal length (cm)', 'petal width (cm)'],
        key='data_nest')
