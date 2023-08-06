from typing import Tuple
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import pytz

from ts_forecasting_pipeline.speccing import ObjectSeriesSpecs
from ts_forecasting_pipeline.modelling import ModelState, create_fitted_model
from ts_forecasting_pipeline.featuring import construct_features
from ts_forecasting_pipeline.utils import get_closest_quarter


"""
Functionality for making predictions per time slot.
"""


def make_forecast_for(
    time_step: datetime, model_state: ModelState
) -> Tuple[float, ModelState]:
    """
    Make a forecast for the time slot.
    May create a model if the previous one is outdated.
    Returns a dict with horizons mapping to forecasted values, as well as the latest valid model.
    """
    if time_step.tzinfo is None:
        time_step.replace(tzinfo=pytz.utc)
    model, specs = model_state.split()
    # create model if old one is outdated.
    if time_step - specs.creation_time > specs.remodel_frequency:
        print("Fitting new model before predicting %s ..." % time_step)
        model = create_fitted_model(specs, "")
        specs.creation_time = time_step
    prediction = model.predict(
        np.hstack(construct_features(time_step, specs).values[0][1:])
    )
    print("Predicting for %s: %.2f" % (time_step, prediction))
    return prediction, ModelState(model, specs)


def make_rolling_forecasts(
    start: datetime, end: datetime, model_state: ModelState
) -> Tuple[pd.Series, ModelState]:
    """
    Repeatedly call make_forecast - for all time steps the desired time window.
    The time window of the specs (training + test data) is moved forwards also step by step.
    Will fail if series specs do not allocate enough data.
    Return Pandas.Series as result, as well as the last ModelState.
    """
    # Prepare time range
    for dt in (start, end):
        if dt.tzinfo is None:
            dt.replace(tzinfo=pytz.utc)
    start = get_closest_quarter(start)
    end = get_closest_quarter(end)

    model, specs = model_state.split()

    # load data from any source only once (i.e. reduce calls to DB or reading in pickles)
    # TODO: copy original series specs, attach them at the end with updated start and end
    # orig_outcome_var = deepcopy(specs.outcome_var)
    # orig_regressors = [deepcopy(r) for r in specs.regressors]

    specs.outcome_var = ObjectSeriesSpecs(
        name=specs.outcome_var.name, data=specs.outcome_var.load_series()
    )
    specs.regressors = [
        ObjectSeriesSpecs(name=r.name, data=r.load_series()) for r in specs.regressors
    ]

    values = pd.Series(index=pd.date_range(start, end, freq="15T"))
    time_step = start
    while time_step < end:
        value, model_state = make_forecast_for(time_step, ModelState(model, specs))
        values[time_step] = value
        # move the model specs one time step further
        specs.start_of_training_data = specs.start_of_training_data + timedelta(
            minutes=15
        )
        specs.end_of_test_data = specs.end_of_test_data + timedelta(minutes=15)
        time_step = time_step + timedelta(minutes=15)

    return values, ModelState(model, specs)
