
'Preprocessing module.\n\nThis module provides a number of preprocessing methods to further clean the data retrieved from the Cognite API.\n'
import math
import warnings
from functools import reduce
import numpy as np
import pandas as pd

def _merge_dataframes(df1, df2):
    if (df1 is None):
        return df2
    if (df2 is None):
        return df1
    return pd.merge(df1, df2, on='timestamp', how='outer').sort_values(by='timestamp').reset_index(drop=True)

def merge_list_of_dataframes(dataframes):
    'Merges together a list of dataframes and creates a time index with evenly spaced intervals.\n\n    Adds NaN to timestamps with missing values.\n\n    Args:\n        dataframes (list(pandas.DataFrame)):  Input dataframes.\n\n    Returns:\n        pandas.DataFrame: Dataframes merged into one with evenly spaced intervals.\n    '
    df_merged = reduce((lambda x, y: _merge_dataframes(x, y)), dataframes)
    df_even_index = make_index_even(df_merged)
    return df_even_index

def make_index_even(dataframe):
    'Creates time index with evenly spaced intervals. Adds NaN to timestamps with missing values.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n\n    Returns:\n        pandas.DataFrame: Input dataframe with evenly spaced intervals.\n    '
    timestamps = dataframe.timestamp.values
    start_time = timestamps[0]
    end_time = timestamps[(- 1)]
    deltas = np.diff(timestamps, 1)
    delta = reduce((lambda x, y: math.gcd(x, y)), deltas)
    t_new = np.arange(start_time, (end_time + delta), delta)
    new_df = pd.DataFrame(t_new, columns=['timestamp'])
    return new_df.merge(dataframe, on='timestamp', how='outer').sort_values(by='timestamp').reset_index(drop=True)

def fill_nan(dataframe):
    'Uses step interpolation to replace NaN values with the previous non-NaN value.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n\n    Returns:\n        pandas.DataFrame: Input dataframe with NaN values removed by forward fill.\n    '
    return dataframe.fillna(method='ffill')

def remove_nan_columns(dataframe):
    'Removes columns of data frame where any value is NaN.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n\n    Returns:\n        tuple: tuple containing:\n            pandas.DataFrame: Dataframe with columns containing NaN values removed.\n            numpy.array: Array of bools indicating which columns were kept.\n    '
    df_copy = dataframe.set_index('timestamp')
    selected_columns_mask = df_copy.notnull().all().values
    return (dataframe.dropna(axis=1, how='any'), selected_columns_mask)

def normalize(dataframe):
    'Centers and scales each column in the data frame to zero mean and unit variance.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n\n    Returns:\n        pandas.DataFrame: Normalized dataframe.\n    '
    dataframe = dataframe.set_index('timestamp')
    dataframe = ((dataframe - dataframe.mean()) / dataframe.std())
    return dataframe.reset_index()

def remove_zero_variance_columns(dataframe):
    'Removes columns with zero variance.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n\n    Returns:\n        tuple: tuple containing:\n            pandas.DataFrame: Dataframe with zero-variance columns removed.\n            numpy.array: Array of bools indicating which columns were kept.\n    '
    dataframe = dataframe.set_index('timestamp')
    selected_columns_mask = (dataframe.var().values > 0)
    dataframe = dataframe.loc[:, selected_columns_mask].reset_index()
    return (dataframe, selected_columns_mask)

def preprocess(dataframe, remove_leading_nan_rows=False, center_and_scale=False):
    'Performs a series of preprocessing steps on the given dataframe.\n\n    1) Creates an evenly spaced time index\n    2) Forward fills NaN values\n    3) Either removes leading rows with nan values or removes columns with leading nan values\n    4) Removes columns with zero variance\n    5) Optionally centers and scales the dataframe to zero mean and unit variance.\n\n    Args:\n        dataframe (pandas.DataFrame):  Input dataframe.\n        remove_leading_nan_rows (bool, optional): Whether or not to skip leading rows containing NaN values.\n        center_and_scale (bool, optional): Whether or not to normalize the data.\n\n    Returns:\n        tuple: tuple containing:\n            pandas.DataFrame: Dataframe with zero-variance columns removed.\n            numpy.array: Array of bools indicating which columns were kept.\n    '
    dataframe = make_index_even(dataframe)
    dataframe = fill_nan(dataframe)
    if remove_leading_nan_rows:
        dataframe.dropna(axis=0, how='any', inplace=True)
    if dataframe.isnull().sum().values.sum():
        warning = 'Some columns contain leading NaN-values after forward-fill. Columns {} will be removed.\nConsider setting the skip_leading_nan_rows parameter to True in order to remove leading rows with NaN values.'.format(dataframe.columns[dataframe.isnull().any().values].values)
        warnings.warn(warning)
    (_, selected_columns_mask_nan) = remove_nan_columns(dataframe)
    (_, selected_columns_mask_zero_var) = remove_zero_variance_columns(dataframe)
    selected_columns_mask = np.logical_and(selected_columns_mask_nan, selected_columns_mask_zero_var)
    dataframe = dataframe.set_index('timestamp').loc[:, selected_columns_mask].reset_index()
    if center_and_scale:
        dataframe = normalize(dataframe)
    return (dataframe, selected_columns_mask)
