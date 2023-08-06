import pandas as pd
from tidyframe import rolling


def test_rolling_positive():
    a = list(range(10))
    pd.DataFrame({'a': a, 'b': rolling(a, 3)})


def test_rolling_negative():
    a = list(range(10))
    pd.DataFrame({'a': a, 'b': rolling(a, -3)})
