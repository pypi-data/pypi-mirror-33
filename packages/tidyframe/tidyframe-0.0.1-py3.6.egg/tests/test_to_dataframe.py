import pandas as pd
from tidyframe import to_dataframe

list_series = [
    pd.Series([1, 2], index=['i_1', 'i_2']),
    pd.Series([3, 4], index=['i_1', 'i_2'])
]
list_series2 = [
    pd.Series([1, 2], index=['i_1', 'i_2']),
    pd.Series([3, 4], index=['i_3', 'i_4'])
]


def test_to_dataframe_basic():
    assert to_dataframe(list_series).shape == (2, 3)


def test_to_dataframe_index():
    assert to_dataframe(list_series2).shape == (2, 5)


def test_to_dataframe_index_name():
    df = to_dataframe(list_series, index_name='index2')
    assert 'index2' in df.columns.tolist()
