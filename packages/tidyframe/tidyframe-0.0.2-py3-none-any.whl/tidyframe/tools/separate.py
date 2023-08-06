""" Separate string list to Pandas DataFrame """

import pandas as pd
import numpy as np


def _select_index(x, i, otherwise=np.NaN):
    """
    Select by index and Catch all Exception

    Parameters
    ----------
    x : array
    i : index
    otherwise : fill value if exist exception

    Returns
    -------
    x[i] if not exception happen else return otherwise
    """
    try:
        return x[i]
    except:
        return otherwise


def separate(series, index=None, columns=None, otherwise=np.NaN):
    """
    Separate string list to Pandas DataFrame

    Parameters
    ----------
    series : list of list or Series of list
    index : filter return index
    columns : return column name of DataFrame
    otherwise : numpy.NaN, fill value of not exist value

    Returns
    -------
    df_return : Pandas DataFrame with split each element of series to column
    """
    series = pd.Series(series)
    ncol = series.apply(len).max()
    if index is not None:
        assert max(index) < ncol, 'max of index MUST less than max of Series'
        if columns is not None:
            assert len(columns) == len(
                index), "length of columns MUST SAME as length of index"
        else:
            columns = pd.Series(
                ['col'] * len(index)) + '_' + pd.Series(index).apply(str)
    else:
        index = list(range(ncol))
        columns = pd.Series(['col'] * ncol) + '_' + pd.Series(
            range(ncol)).apply(str)
    return_df = pd.DataFrame()

    for i, name in zip(index, columns):
        return_df[name] = series.apply(
            lambda x: _select_index(x, i, otherwise))
    return return_df
