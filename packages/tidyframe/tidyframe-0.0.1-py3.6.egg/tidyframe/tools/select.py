""" Easy Select Column Method from Pandas DataFrame """

import re
from copy import copy, deepcopy


def select(df,
           columns=None,
           columns_minus=None,
           columns_between=None,
           copy=False):
    """
    Select Pandas DataFrame by minus

    Parameters
    ----------
    df : Pandas DataFrame
    columns_minus : column which want to remove
    copy : whether return deep copy DataFrame

    Returns
    -------
    df_return : Pandas DataFrame
    """
    if columns is not None:
        df_return = df[columns]
    if columns_minus is not None:
        raw_col = {value: i for i, value in enumerate(df.columns)}
        for pop_key in columns_minus:
            raw_col.pop(pop_key)
        df_return = df[list(raw_col.keys())]
    if columns_between is not None:
        columns_location = {column: i for i, column in enumerate(df.columns)}
        assert columns_location[columns_between[0]] < columns_location[columns_between[1]], 'first column location must less than second column location'
        df_return = df.iloc[:,
                            range(columns_location[columns_between[0]],
                                  columns_location[columns_between[1]] + 1)]
    if copy:
        return deepcopy(df_return)
    else:
        return df_return


def reorder_columns(df, columns=None, pattern=None):
    """
    reorder columns of pandas DataFrame

    Parameters
    ----------
    df : Pandas DataFrame
    columns : list which want to head column name(non-use if pattern is not None)
    pattern : regular expression pattern which let selected columns be at head columns

    Returns
    -------
    df_return : Pandas DataFrame
    """
    if pattern:
        reorder_columns = list(
            filter(lambda x: re.search(pattern, x), df.columns))
    else:
        reorder_columns = copy(list(columns))
    raw_columns = df.columns.copy()
    reorder_columns.extend(raw_columns.difference(reorder_columns).tolist())
    return df[reorder_columns]
