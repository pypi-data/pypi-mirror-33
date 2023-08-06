"""
functionality to create the feature data necessary.
"""
from typing import List

import pandas as pd


def construct_dataframe(variable_containers):
    """
    variable_containers: list of tuples
    each tuple should contain : df, name of column in df, new name of column in resultin df
    data frame is created based on the index of input
    """
    dict_for_df = {}
    for variable_container in variable_containers:
        new_name = variable_container[2]
        cur_name = variable_container[1]
        df_data = variable_container[0]
        dict_for_df[new_name] = df_data[cur_name]
    df = pd.DataFrame(dict_for_df)
    return df


def convert_lag_to_name_str(lag):
    if lag < 0:
        str_lag = "l" + str(abs(lag))
    else:
        str_lag = "f" + str(abs(lag))
    return str_lag


def add_lags(df: pd.DataFrame, column: str, lags: List[int], inplace=True):
    """
    df: DataFrame 
    Contains data with the contains columns to lag

    column: str
    The column with the data to lag

    lags: list
    lags in days. negative means a lag, positive is a future value

    inplace: Bool


    Creates lag columns for a column in the dataframe (inplace)
    Negative values are lags, while positive values are future values
    The new columns are named like the lagged column, plus "_l<lag>".
    In case of positive 'lags' (future values), new columns are named like the lagged column, plus "_f<lag>".

    TODO: hardcoded the time interval (15 minutes), in case of other interval or missing rows, it does not return right value
    """
    if inplace == False:
        df = df.copy()

    for lag in lags:
        str_lag = convert_lag_to_name_str(lag)

        df[column + "_" + str_lag] = df[column].shift(-96 * lag)

    if inplace == False:
        return df


### note hendrik: don't fully understand this function. I created construct_dataframe(), does that replace this function?
def add_regressors(df: pd.DataFrame, name: str, horizons: List[str]):
    """
    Get regressor data to be added to df, in form of forecasted data.
    """
    # Calls forecasting.get_forecasts() on a specific pickle or table
    pass
