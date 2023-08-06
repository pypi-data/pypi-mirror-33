from typing import Dict, Tuple, Optional, Sequence
from datetime import datetime

import pandas as pd
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt

from ts_forecasting_pipeline.speccing import ModelSpecs
from ts_forecasting_pipeline.featuring import construct_features
from ts_forecasting_pipeline.serializing import save_model
from ts_forecasting_pipeline import MODEL_TYPES, ModelState


"""
Functions for working with time series models.
"""


def create_fitted_model(
    specs: ModelSpecs, version: str, save: bool = False
) -> MODEL_TYPES:
    """
    Create a new fitted model with the given specs.
    If needed, the fitted model and specs can be persisted to file. From there, they can be loaded back with
    load_model.

    TODO: frequency of 15T is still hardcoded.
    """
    regression_frame = construct_features(purpose="train", specs=specs)

    # Remove any observation where data is missing.
    # Other parts of the workflow cannot handle missing data, so everything should be verified here.
    regression_frame = regression_frame[~pd.isnull(regression_frame).any(axis=1)]

    x_train = regression_frame.iloc[:, 1:]
    y_train = np.array(regression_frame.iloc[:, 0])

    if specs.model_type == "OLS":
        model = sm.OLS(y_train, x_train)
    else:
        raise Exception("Unknown model type: %s " % specs.model_type)

    fitted_model = model.fit()

    if save:
        save_model(ModelState(fitted_model, specs), version)

    return fitted_model


def evaluate_models(
    m1: ModelState, m2: Optional[ModelState] = None, plot_path: str = None
):
    """
    Run a model or two against test data and plot results.
    Useful to judge model performance or compare two models.
    Shows RMSE values, plots error distributions and prints the time it took to forecast.

    TODO: support testing m2 next to m1
    """
    fitted_m1, m1_specs = m1.split()

    regression_frame = construct_features(purpose="test", specs=m1_specs)

    x_test = regression_frame.iloc[:, 1:]
    y_test = np.array(regression_frame.iloc[:, 0])

    y_hat_test = fitted_m1.predict(x_test)
    print(
        "rmse = %s"
        % (str(round(sm.tools.eval_measures.rmse(y_test, y_hat_test, axis=0), 4)))
    )

    plot_true_versus_predicted(
        regression_frame.index, y_test, y_hat_test.values, plot_path
    )

    plot_error_graph(y_test, y_hat_test, plot_path=plot_path)


def plot_true_versus_predicted(
    indices: pd.DatetimeIndex,
    true_values: Sequence[float],
    predicted_values: Sequence[float],
    plot_path: str = None,
):
    """
    Helper function to plot real values next to forecasted values.
    """
    plt.plot(indices.to_pydatetime(), true_values, label="actual")
    plt.plot(indices.to_pydatetime(), predicted_values, label="predicted")
    plt.xlabel("tested time steps")
    plt.ylabel("values")
    plt.legend()
    if plot_path is None:
        plt.show()
    else:
        plt.savefig(plot_path + "/true_versus_predicted.png")
        plt.close()


def plot_error_graph(
    true_values: Sequence[float],
    predicted_values: Sequence[float],
    use_abs_errors: bool = False,
    plot_path: str = None,
):

    results_df = pd.DataFrame({"y_hat_test": predicted_values, "y_test": true_values})

    # remove 0 s
    results_df = results_df[(results_df != 0).all(1)]

    results_df["max_error"] = abs(results_df.y_hat_test / results_df.y_test - 1)
    if use_abs_errors is True:
        #  if you want to look at abs values, instead of (abs)proportional errors
        results_df["max_error"] = abs(results_df.y_hat_test - results_df.y_test)

    results_df.sort_values("max_error", inplace=True)
    results_df["proportion"] = (np.arange(len(results_df)) + 1) / len(results_df)

    plt.plot(results_df["max_error"], results_df["proportion"], "-o")
    plt.ylim(0, 1)
    plt.xlim(0, 1)
    plt.xlabel("max error for proportion")
    plt.ylabel("proportion of observations")
    if plot_path is None:
        plt.show()
    else:
        plt.savefig(plot_path + "/error_graph.png")
        plt.close()


def model_param_grid_search(
    df: pd.DataFrame,
    start_of_training_data: datetime,
    end_of_test_data: datetime,
    params: Dict[str, Tuple[float, float]],
) -> Dict[str, float]:

    """
    Creates and tests models with different model parameters.
    Returns the best parameter set w.r.t. smallest RMSE.
    """
    return {}
