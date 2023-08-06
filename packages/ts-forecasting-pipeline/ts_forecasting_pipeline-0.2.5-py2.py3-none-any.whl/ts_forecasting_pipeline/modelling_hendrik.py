from typing import List, Dict, Tuple, Optional, Union
import datetime
import featuring_hendrik as featuring
import pandas as pd
from statsmodels import regression
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt
import pickle
from os import listdir

"""
Functions for working with time series models.
TODO: store the exact circumstances of a model, like lags and regressors somewhere, so we can easily know how to create
fitting feature vectors. For now, we'll hardcode those.
"""

# Here we can list any class we might use. They all can be expected to have a fit() and a predict(X) method.
MODEL_CLASS = Union[regression.linear_model.OLS]

RATIO_TRAINING_TEST_DATA = 2 / 3


def load_model(outcome, model_dir):
    dir_list = listdir(model_dir)
    relevant_models = [s for s in dir_list if "model_" + outcome in s]
    model_name = sorted(relevant_models)[-1]
    print("loading model: %s" % (model_name))
    return pickle.load(open("/".join([model_dir, model_name]), "rb"))

    ## note that the variable containers include the data, loading them again in the notebook does not work right atm
    ## should be fixed asap
    ## so data frame construcor is not saved now


def save_model(model, outcome, model_dir):
    model_name = "_".join(
        [
            "model",
            outcome,
            datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S"),
        ]
    )
    pickle.dump(model, open(model_dir + "/" + model_name + ".sav", "wb"))


def create_model(
    df,
    outcome,
    lags,
    regressors,
    datetime_train,
    training_window,
    include_constant=True,
):
    """ 
    Parameters
    df: DataFrame
    the data

    outcome: str 
    dependent variable. variable to predict
    
    lags: list
    lags to use of outcome for prediction

    regressors: list
    independent variable(s)

    datetime: datetime
    moment up to which data will be used for fitting the model

    training_window: int
    number of days that are used for training the model
    
    NOTES: also only works with 15T freq and no missing variables
    horizon is not specifically mentioned in this function; it is implicit in the number of lags that are provided. This could be more explicit in this function

    """

    traing_start_date = datetime_train - datetime.timedelta(days=training_window)

    ## for checking purpose, hardcode traing_start_date, remove later
    # traing_start_date = datetime.datetime(2015,1,8)

    training_data_indices = pd.date_range(traing_start_date, datetime_train, freq="15T")

    outcome_lags = [
        outcome + "_" + featuring.convert_lag_to_name_str(lag) for lag in lags
    ]

    regression_frame = df[[outcome] + outcome_lags + regressors].loc[
        training_data_indices
    ]
    ## remove any observation where data is missing, other parts of the workflow cannot handle missing data, so everything should be verified
    regression_frame = regression_frame[~pd.isnull(regression_frame).any(axis=1)]
    if include_constant == True:
        regression_frame["constant"] = 1

    X_train = regression_frame.iloc[:, 1:]
    y_train = np.array(regression_frame.iloc[:, 0])

    mod = sm.OLS(y_train, X_train)
    res = mod.fit()
    return res


def plot_error_graph(true_values, predicted_values, use_abs_errors=False):

    results_df = pd.DataFrame({"y_hat_test": predicted_values, "y_test": true_values})

    ## remove 0 s
    results_df = results_df[(results_df != 0).all(1)]

    results_df["max_error"] = abs(results_df.y_hat_test / results_df.y_test - 1)
    if use_abs_errors == True:
        ## if you want to look at abs values, instead of (abs)proportional errors
        results_df["max_error"] = abs(results_df.y_hat_test - results_df.y_test)

    results_df.sort_values("max_error", inplace=True)
    results_df["proportion"] = (np.arange(len(results_df)) + 1) / len(results_df)

    plt.plot(results_df["max_error"], results_df["proportion"], "-o")
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.xlabel("max error for proportion")
    plt.ylabel("proportion of observations")


def test_model(
    model,
    df,
    outcome,
    lags,
    regressors,
    datetime_first_test,
    testing_window,
    include_constant=True,
    return_fitted_values=False,
):

    testing_end_date = datetime_first_test + datetime.timedelta(days=testing_window)

    ## for checking purpose, hardcode traing_start_date, remove later
    # testing_end_date = datetime.datetime(2015,4,15,3,45)

    testing_data_indices = pd.date_range(
        datetime_first_test, testing_end_date, freq="15T"
    )

    outcome_lags = [
        outcome + "_" + featuring.convert_lag_to_name_str(lag) for lag in lags
    ]

    regression_frame = df[[outcome] + outcome_lags + regressors].loc[
        testing_data_indices
    ]

    if include_constant == True:
        regression_frame["constant"] = 1

    X_test = regression_frame.iloc[:, 1:]
    y_test = np.array(regression_frame.iloc[:, 0])

    y_hat_test = model.predict(X_test)
    print(
        "rmse = %s"
        % (str(round(sm.tools.eval_measures.rmse(y_test, y_hat_test, axis=0), 4)))
    )

    plot_error_graph(y_test, y_hat_test)

    if return_fitted_values == True:
        return pd.DataFrame({"predicted_values": y_hat_test, "y_test": y_test})


def model_param_grid_search(
    df: pd.DataFrame,
    start_data: datetime,
    end_data: datetime,
    params: Dict[str, Tuple[float, float]],
) -> Dict[str, float]:

    """
    Creates and tests models with different model parameters.
    Returns the best parameter set w.r.t. smallest RMSE.
    """
    return {}
