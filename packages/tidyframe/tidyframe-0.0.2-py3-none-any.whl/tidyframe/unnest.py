import pandas as pd
import copy as cp

def unnest(df, copy=False):
    """Inverse Nest DataFrame
    
    Parameters
    ----------
    df: DataFrame with Series of Dataframe
    """
    df_check = df.applymap(lambda x: isinstance(x, pd.DataFrame))
    columns_nest = df_check.columns[df_check.sum()==df_check.shape[0]].tolist()
    if len(columns_nest) == 1:
        repeat_times = list(map(lambda x: x.shape[0], df[columns_nest[0]]))
        columns_group = df_check.columns.difference(columns_nest)
        df_return = pd.DataFrame(df2[columns_group].as_matrix().repeat(repeat_times, axis=0), columns=columns_group)
        df_return = pd.concat([df_return, pd.concat([*df2[columns_nest[0]].tolist()])], axis=1)
        if copy:
            return cp.deepcopy(df_return)
        else:
            return df_return
