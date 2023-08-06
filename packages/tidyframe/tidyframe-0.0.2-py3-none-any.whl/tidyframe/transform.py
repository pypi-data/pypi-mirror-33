""" Convert Pandas DataFrame to nest DataFrame """

import copy as cp
from functools import partial
import pandas as pd
import numpy as np


def nest(df,
         columns=[],
         columns_minus=[],
         columns_between=[],
         key='data',
         copy=False):
    """
    Nest repeated values

    Parameters
    ----------
    df: DataFrameGroupBy or DataFrame
    columns: list or index, nest columns
    columns_minus: list or index, columns which do not want to nest
                   (must choose one of columns and columns_minus)
    columns_between: list with length 2, assigin nest columns between to two columns
    copy: False, return DataFrame using copy.deepcopy
    """
    assert isinstance(df,
                      (pd.core.frame.DataFrame,
                       pd.core.groupby.DataFrameGroupBy)), "Must be DataFrame"
    if len(columns) > 0:
        assert len(columns_minus) == 0 and len(
            columns_between
        ) == 0, "Using Parameter columns then columns_minus and column_between must not use"
    if len(columns_minus) > 0:
        assert len(columns) == 0 and len(
            columns_between
        ) == 0, "Using Parameter columns_minus then columns and columns_between must not use"
    if len(columns_between) > 0:
        assert len(columns_between) == 2, "lenth of columns_between must be 2"
        assert len(columns) == 0 and len(
            columns_minus
        ) == 0, "Using Parameter columns_between then columns_minus and between must not use"

    if isinstance(df, pd.core.frame.DataFrame):
        if len(columns) > 0:
            if isinstance(columns, pd.core.indexes.base.Index):
                columns_nest = columns.tolist()
            else:
                columns_nest = columns
            columns_group = df.columns.difference(columns_nest).tolist()
            df_g = df.groupby(columns_group)
            data = [[index, group[columns_nest]] for index, group in df_g]
        elif len(columns_minus) > 0:
            if isinstance(columns_minus, pd.core.indexes.base.Index):
                columns_group = columns_minus.tolist()
            else:
                columns_group = columns_minus
            columns_nest = df.columns.difference(columns_group).tolist()
            df_g = df.groupby(columns_group)
            data = [[index, group[columns_nest]] for index, group in df_g]
        else:
            index_start = np.where(df.columns == columns_between[0])[0][0]
            index_end = np.where(df.columns == columns_between[1])[0][0]
            assert index_start < index_end, "columns_between order error"
            columns_nest = df.columns[index_start:(index_end + 1)].tolist()
            columns_group = df.columns.difference(columns_nest).tolist()
            df_g = df.groupby(columns_group)
            data = [[index, group[columns_nest]] for index, group in df_g]
    else:
        columns_group = list(df.dtypes.index.names)
        columns_nest = list(df.dtypes.columns)
        data = [[index, group[columns_nest]] for index, group in df]
    outer = list(map(lambda x: x[0], data))
    df_return = pd.DataFrame(outer, columns=columns_group)
    df_return[key] = list(map(lambda x: x[1][columns_nest], data))
    if copy:
        return cp.deepcopy(df_return)
    else:
        return df_return


def unnest(df, drop=[], copy=False):
    """
    Inverse Nest DataFrame

    Parameters
    ----------
    df: DataFrame with Series of Dataframe
    drop: list of column which do not return
    """
    df_check = df.applymap(lambda x: isinstance(x, pd.DataFrame))
    columns_nest = df_check.columns[df_check.sum() == df_check.shape[
        0]].tolist()
    if len(columns_nest) > 0:
        if len(columns_nest) == 1:
            repeat_times = list(map(lambda x: x.shape[0], df[columns_nest[0]]))
            columns_group = df_check.columns.difference(columns_nest)
            df_return = pd.DataFrame(
                df[columns_group].values.repeat(repeat_times, axis=0),
                columns=columns_group)
            df_return = pd.concat(
                [
                    df_return.reset_index(drop=True),
                    pd.concat([*df[columns_nest[0]].tolist()
                               ]).reset_index(drop=True)
                ],
                axis=1)
            if copy:
                return cp.deepcopy(
                    df_return[df_return.columns.difference(drop)])
            else:
                return df_return[df_return.columns.difference(drop)]
        else:
            dict_col = {v: k + 1 for k, v in enumerate(df.columns)}
            columns_value = df.columns.difference(columns_nest).tolist()
            list_df_tmp = []
            for x in df.itertuples():
                df_tmp = pd.concat(
                    [x[dict_col[col]] for col in columns_nest], axis=1)
                for col in columns_value:
                    df_tmp[col] = x[dict_col[col]]
                list_df_tmp.append(df_tmp)
            df_return = pd.concat(list_df_tmp)
            return df_return[pd.Index(columns_value).append(
                df_return.columns.difference(columns_value))]
    else:
        column_series = df.columns[
            df.applymap(lambda x: isinstance(x, (pd.Series, np.ndarray, list)))
            .sum() > 0].tolist()
        assert len(column_series) == 1, "Must exist one list of list Series"
        repeat_times = df[column_series[0]].map(len)
        columns_group = df.columns.difference(column_series)
        df_return = pd.DataFrame(
            df[columns_group].values.repeat(repeat_times, axis=0),
            columns=columns_group)
        df_series = pd.concat(
            [*df[column_series[0]].map(lambda x: pd.DataFrame(x))], axis=0)
        df_return[column_series[0]] = df_series[0].tolist()
        if copy:
            return cp.deepcopy(df_return[df_return.columns.difference(drop)])
        else:
            return df_return[df_return.columns.difference(drop)]


def apply_window(df, func, partition=None, columns=None):
    """ apply window function in DataFrame

    Parameters
    ----------
    df: DataFrameGroupBy or DataFrame
    func: list of function
    partition: list of partition columns
    columns: list of columns which need to apply func
    """
    if isinstance(df, pd.core.groupby.DataFrameGroupBy):
        df_g = df
    else:
        df_g = df.groupby(partition)
    if columns is not None:
        if callable(func):
            if isinstance(columns, str):
                return df_g[columns].transform(func)
            elif isinstance(columns, (list, pd.core.indexes.base.Index)):
                df_return = df_g[columns].transform(func)
                df_return.columns = df_return.columns + "_" + func.__name__
                return df_return
        if isinstance(func, list):
            list_df = []
            df_return = pd.DataFrame()
            for v in func:
                if isinstance(columns, str):
                    return df_g[columns].transform(v)
                df_tmp = df_g[columns].transform(v)
                df_tmp.columns = df_tmp.columns + "_" + v.__name__
                list_df.append(df_tmp)
            return pd.concat(list_df, axis=1)
    if isinstance(func, dict):
        df_return = pd.DataFrame()
        for (k, v) in func.items():
            if isinstance(v, list):
                for each_fun in v:
                    df_return[k + '_' +
                              each_fun.__name__] = df_g[k].transform(each_fun)
            else:
                df_return[k + '_' + v.__name__] = df_g[k].transform(v)
        if isinstance(df, pd.core.frame.DataFrame):
            df_return.index = df.index
        return df_return


def _series_to_dict(x, index_name='index'):
    """
    Change Pandas Series to Dict With Index

    Parameters
    ----------
    x : pandas Series
    index_name : return dict key of index name
    """
    x_dict = x.to_dict()
    x_dict[index_name] = x.name
    return x_dict


def to_dataframe(data, index_name='index'):
    """
    Change list of Pandas Serice to Pandas DataFrame

    Parameters
    ----------
    data : list of pandas Series
    index_name : return index DataFrame column name
    """
    p_series_to_dict = partial(_series_to_dict, index_name=index_name)
    return pd.DataFrame(list(map(p_series_to_dict, data)))


def rolling(list_object, window_size, missing=np.NaN):
    assert isinstance(list_object,
                      list), "type of list_object must be equal list"
    assert window_size != 0, "window_size must be not equal zero"
    list_return = []
    if window_size > 0:
        for i, x in enumerate(list_object):
            if i < (window_size - 1):
                ele_list = [missing] * window_size
                ele_list[-1 * (i + 1):] = list_object[0:(i + 1)]
                list_return.append(ele_list.copy())
            else:
                list_return.append(list_object[(i - window_size + 1):i + 1])
        return list_return
    else:
        len_object = len(list_object)
        len_end = 1
        for i, x in enumerate(list_object):
            if i > (len_object + window_size):
                ele_list = list_object[i:len_object].copy()
                ele_list.extend([missing] * (len_end))
                list_return.append(ele_list.copy())
                len_end = len_end + 1
            else:
                list_return.append(list_object[i:i - window_size])
        return list_return
