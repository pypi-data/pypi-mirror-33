import pandas as pd
from tidyframe.tools import combination

df_a = pd.DataFrame({'a1': list('ABC'), 'a2': list('CDE')})
df_b = pd.DataFrame({'b1': list('01234'), 'b2': list('56789')})
df_c = pd.DataFrame({'c1': list('pq'), 'c2': list('rs')})
df_d = pd.DataFrame({'d1': list('abcd'), 'd2': list('efgh')})
df_d.index.name = 'index'


def test_combination_basic():
    combination([df_a, df_b, df_c])


def test_combination_basic_2():
    combination([df_a, df_b, df_d])
