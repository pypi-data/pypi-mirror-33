import pandas as pd
import copy as cp

def nest(df, *args, key='data', copy=False):
    """Nest repeated values
    
    Parameters
    ----------
    df: DataFrame of pansas'
    *args: nest columns
    copy: weather return DataFrame using copy.deepcopy
    """
    assert len(set(args) - set(df.columns))==0, 'Unknown Columns'
    columns_nest = df.columns.difference(args)
    columns_group = df.columns.difference(columns_nest).tolist()
    df_g = df.groupby(columns_group)
    data = [[index ,group[columns_nest]] for index, group in df_g]
    outer = list(map(lambda x: x[0], data))
    df_return = pd.DataFrame(outer, columns=columns_group)
    df_return[key] = list(map(lambda x: x[1][columns_nest], data))
    if copy:
        return cp.deepcopy(df_return)
    else:
        return df_return
