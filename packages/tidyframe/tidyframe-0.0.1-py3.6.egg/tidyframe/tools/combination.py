""" All combination rows from list of DataFrame """

import pandas as pd


def combination(dfs):
    """
    All combination rows from list of DataFrame

    Parameters
    ----------
    dfs : list of Pandas DataFrame

    Returns
    -------
    df_return : Pandas DataFrame
    """
    dfs_index_name = [
        df.index.name if df.index.name else 'index' for df in dfs
    ]
    dfs = [
        df.reset_index().rename(
            columns={dfs_index_name[i]: dfs_index_name[i] + "_" + str(i)})
        if dfs_index_name[i] == 'index' else df.reset_index()
        for i, df in enumerate(dfs)
    ]
    join_key = list(pd.compat.product(*[df.index for df in dfs]))
    list_combine_df = []
    for i, df in enumerate(dfs):
        list_combine_df.append(
            dfs[i].iloc[[x[i] for x in join_key], :].reset_index())
    df_return = pd.concat(list_combine_df, axis=1, ignore_index=False)
    del df_return['index']
    return df_return
