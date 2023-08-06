import pandas as pd
from tidyframe.tools import flatten_dict, reorder_columns

dict_1 = {
    'a': 1,
    'b': [1, 2],
    'c': {
        'cc1': 3,
        'cc2': 4
    },
    'd': {
        'd1': 5,
        'd2': {
            'dd1': 6,
            'dd2': 7
        }
    }
}
dict_2 = {
    'a': 1,
    'b': [1, 2],
    'c': {
        'cc1': 3
    },
    'd': {
        'd1': 5,
        'd2': {
            'dd1': 6,
            'dd2': 7
        }
    }
}
list_dict = [dict_1, dict_2]
df = pd.DataFrame([flatten_dict(x) for x in list_dict])


def test_basic_reorder_columns():
    columns = ['d_d2_dd1', 'd_d2_dd2']
    reorder_columns(df, columns)


def test_basic_reorder_columns_pattern():
    reorder_columns(df, pattern='^d')
