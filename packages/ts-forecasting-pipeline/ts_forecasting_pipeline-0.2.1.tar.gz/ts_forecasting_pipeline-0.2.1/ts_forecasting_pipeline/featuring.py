"""
functionality to create the feature data necessary.
"""
from typing import List, Optional, Union
from datetime import datetime, timedelta

import pandas as pd
import statsmodels.api as sm

from ts_forecasting_pipeline.speccing import ModelSpecs
from ts_forecasting_pipeline.utils import get_closest_quarter


def construct_features(
    purpose: Union[datetime, str], specs: ModelSpecs
) -> pd.DataFrame:
    """
    Create a DataFrame based on ModelSpecs. This means loading data, potentially running a custom transformation,
    adding lags & returning only the relevant date rows.
    Purpose is either "train" or "test" (which influences for which time steps to load features),
    or a datetime object for which we need the features (useful for predicting).
    """

    if not (
        isinstance(purpose, datetime)
        or (isinstance(purpose, str) and purpose in ("train", "test"))
    ):
        raise Exception(
            "Purpose for dataframe construction needs to be either 'train', 'test' or a time_step (datetime object)."
        )

    df = pd.DataFrame()

    # load raw data series
    df[specs.outcome_var.name] = specs.outcome_var.load_series()
    for reg_spec in specs.regressors:
        df[reg_spec.name] = reg_spec.load_series()

    datetime_indices = get_time_steps(purpose, specs)

    # add lags on the outcome var
    add_lags(df, specs.outcome_var.name, specs.lags, inplace=True)

    # perform the custom transformation, if needed
    if specs.transform is not None:
        df = specs.transform(df)

    outcome_lags = [
        lag_name
        for lag_name in [
            specs.outcome_var.name + "_" + lag_to_suffix(lag) for lag in specs.lags
        ]
        if lag_name in df.columns
    ]

    # now select only relevant columns and relevant datetime indices
    relevant_columns = (
        [specs.outcome_var.name] + outcome_lags + [r.name for r in specs.regressors]
    )

    df = df[relevant_columns].loc[datetime_indices]

    # if specs.model_type == "OLS":
    #    df = sm.add_constant(df)

    return df


def get_time_steps(
    purpose: Union[str, datetime], specs: ModelSpecs
) -> pd.DatetimeIndex:
    """ get relevant datetime indices to build features for."""
    if isinstance(purpose, datetime):
        return pd.date_range(purpose, purpose, freq="15T")

    length_of_data = specs.end_of_test_data - specs.start_of_training_data
    datetime_indices = None
    if purpose == "train":
        end_of_training_data = get_closest_quarter(
            specs.start_of_training_data
            + length_of_data * specs.ratio_training_test_data
        )
        print("Start of training: %s" % specs.start_of_training_data)
        print("End of training: %s" % end_of_training_data)
        datetime_indices = pd.date_range(
            specs.start_of_training_data, end_of_training_data, freq="15T"
        )
    elif purpose == "test":
        start_of_testing_data = get_closest_quarter(
            specs.start_of_training_data
            + (length_of_data * specs.ratio_training_test_data)
            + timedelta(minutes=15)
        )
        print("Start of testing: %s" % start_of_testing_data)
        print("End of testing: %s" % specs.end_of_test_data)
        datetime_indices = pd.date_range(
            start_of_testing_data, specs.end_of_test_data, freq="15T"
        )

    return datetime_indices


def lag_to_suffix(lag: int) -> str:
    """
    Return the suffix for a column, given its lag.
    """
    if lag < 0:
        str_lag = "f" + str(abs(lag))
    else:
        str_lag = "l" + str(abs(lag))
    return str_lag


def add_lags(
    df: pd.DataFrame,
    column: str,
    lags: List[int],
    name_as: str = "quarter_hour",
    inplace: bool = True,
) -> Optional[pd.DataFrame]:
    """
    Creates lag columns for a column in the dataframe. Lags are in fifteen minute steps (15T).
    Positive values are lags, while negative values are future values.
    The new columns are named like the lagged column, plus "_l<lag>" (or "_f<lag>" for positive lags (future values)),
    where <lag> is the 15-minute lag value or the translation of it into days, weeks or years.
    In case of positive 'lags' (future values), new columns are named like the lagged column, plus "_f<lag>".

    TODO: We could also review if using statsmodels.tsa.tsatools.add_lag is of interest, but here self-made is probably
          what we need.
    """
    if inplace is False:
        df = df.copy()

    lag_names = [l for l in lags]
    if name_as == "hour":
        lag_names = [int(l / 4) for l in lags]
    if name_as == "day":
        lag_names = [int(l / 96) for l in lags]
    if name_as == "week":
        lag_names = [int(l / 96 / 7) for l in lags]
    if name_as == "year":
        lag_names = [int(l / 96 / 365) for l in lags]

    for lag in lags:
        lag_name = lag_names[lags.index(lag)]
        df[column + "_" + lag_to_suffix(lag_name)] = df[column].shift(lag)

    if inplace is False:
        return df
