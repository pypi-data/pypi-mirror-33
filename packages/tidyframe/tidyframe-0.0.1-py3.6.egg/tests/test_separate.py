import pandas as pd
import numpy as np
from tidyframe.tools import separate

df = pd.DataFrame(
    {
        'full_string': ['a b c d e z', 'f g h i']
    }, index=['row_1', 'row_2'])
series = df.full_string.str.split(' ')


def test_separate_basic():
    separate(series)


def test_separate_index():
    separate(series, index=[0, 4])


def test_separate_using_otherwise():
    separate(series, index=[0, 4], otherwise='otherwise')


def test_separate_change_column_name():
    separate(series, index=[0, 3], columns=['zero', 'three'])


def test_separate_list_to_dataframe():
    separate([list('abc'), list('def')])
