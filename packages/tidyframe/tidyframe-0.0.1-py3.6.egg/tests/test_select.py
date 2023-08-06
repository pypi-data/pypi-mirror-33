from tidyframe import tools
import pandas as pd
import numpy as np

df = pd.DataFrame(
    np.array(range(10)).reshape(2, 5),
    columns=list('abcde'),
    index=['row_1', 'row_2'])


def test_select_basic():
    tools.select(df, columns=['b', 'd'])


def test_select_columns_minus():
    tools.select(df, columns_minus=['b', 'd'])


def test_select_deepcopy():
    tools.select(df, columns_minus=['b', 'd'], copy=True)


def test_select_columns_minus():
    tools.select(df, columns_minus=['b', 'd'])


def test_select_columns_between():
    tools.select(df, columns_between=['b', 'd'])
