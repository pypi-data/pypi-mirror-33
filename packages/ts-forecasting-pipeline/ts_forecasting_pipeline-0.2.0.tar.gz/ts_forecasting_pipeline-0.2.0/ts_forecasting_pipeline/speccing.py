from typing import List, Optional, Callable, Union
from datetime import datetime, timedelta, tzinfo
from pprint import pformat
import json

import pytz
import dateutil.parser
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query

from ts_forecasting_pipeline.utils import tz_aware_utc_now


DEFAULT_RATIO_TRAINING_TEST_DATA = 2 / 3
DEFAULT_REMODELING_FREQUENCY = timedelta(days=1)


class SeriesSpecs(object):
    """Describes a time series (e.g. a pandas Series).
    In essence, a column in the regression frame, filled with numbers.

    Using this class, the column will be filled with NaN values.

    If you have data to be loaded in automatically, you should be using one of the subclasses, which allow to describe
    or pass in an actual data source to be loaded.

    When dealing with columns, our code should usually refer to this superclass so it does not need to care
    which kind of data source it is dealing with.
    """

    # The name in the resulting feature frame, and possibly in the saved model specs (named by outcome var)
    name: str
    # The name in the data source, if source is a pandas DataFrame or database Table - if None, the name will be tried
    column: Optional[str]
    # timezone of the data - useful when de-serializing (e.g. pandas serialises to UTC)
    original_tz: tzinfo

    def __init__(self, name: str, column: str = None, original_tz: tzinfo = None):
        self.name = name
        self.column = column
        if self.column is None:
            self.column = name
        self.original_tz = original_tz
        self.__series_type__ = self.__class__.__name__

    def as_dict(self):
        return vars(self)

    def load_series(self) -> pd.Series:
        return pd.Series()

    def __repr__(self):
        return "%s: <%s>" % (self.__class__.__name__, self.as_dict())


class ObjectSeriesSpecs(SeriesSpecs):
    """
    Spec for a pd.Series object that is being passed in and is stored directly in the specs.
    The data is not mutatable after creation.
    Note: The column argument is not used, as the series has only one column.
    """

    data: pd.Series

    def __init__(
        self, data: pd.Series, name: str, column: str = None, original_tz: tzinfo = None
    ):
        super().__init__(name, None, original_tz)
        self.data = data
        self.original_tz = data.index.tzinfo
        if self.original_tz is None:
            self.original_tz = pytz.utc

    def load_series(self) -> pd.Series:
        return self.data


class DFFileSeriesSpecs(SeriesSpecs):
    """
    Spec for a pandas DataFrame source.
    This class holds the filename, from which we unpickle the data frame, then read the column.
    """

    file_path: str

    def __init__(
        self, file_path: str, name: str, column: str = None, original_tz: tzinfo = None
    ):
        super().__init__(name, column, original_tz)
        self.file_path = file_path

    def load_series(self) -> pd.Series:
        df: pd.DataFrame = pd.read_pickle(self.file_path)
        if df.index.tzinfo is None:
            self.original_tz = pytz.utc
            df.index = df.index.tz_localize(self.original_tz)
        else:
            self.original_tz = df.index.tzinfo
        return df[self.column]


class DBSeriesSpecs(SeriesSpecs):

    """Define how to query a database for time series values.
    This works via a SQLAlchemy query.
    This query should return the needed information for the forecasting pipeline:
    A "datetime" column (which will be set as index) and the values column (named by name or column,
    see SeriesSpecs.__init__, defaults to "value"). For example:
    TODO: show an example"""

    db: Engine
    query: Query

    def __init__(
        self,
        db_engine: Engine,
        query: Query,
        name: str = "value",
        column: str = None,
        original_tz: tzinfo = pytz.utc,  # postgres stores naive datetimes
    ):
        super().__init__(name, column, original_tz)
        self.db_engine = db_engine
        self.query = query

    def load_series(self) -> pd.Series:
        series_orig = pd.read_sql(
            self.query.statement, self.db_engine, parse_dates=["datetime"]
        )
        series_orig.set_index("datetime", drop=True, inplace=True)
        if series_orig.index.tzinfo is None:
            if self.original_tz is not None:
                series_orig.index = series_orig.index.tz_localize(self.original_tz)
        else:
            series_orig.index = series_orig.index.tz_convert(self.original_tz)
        series = series_orig.resample("15T").mean()
        return series["value"]


transform_type = Optional[Callable[[pd.DataFrame], pd.DataFrame]]


class ModelSpecs(object):
    """Describes a model and how it was trained.
    """

    outcome_var: SeriesSpecs
    model_type: str  # e.g. OLS, ARIMA, ...
    lags: List[int]
    regressors: List[SeriesSpecs]
    # Start of training data set
    start_of_training_data: datetime
    # End of testing data set
    end_of_test_data: datetime
    # This determines the cutoff point between training and testing data
    ratio_training_test_data: float
    # time this model was created, defaults to UTC now
    creation_time: datetime
    valid_until: datetime
    model_filename: str
    remodel_frequency: timedelta
    # Custom transformation to perform on the data. Called after all SeriesSpecs were resolved.
    transform: transform_type

    def __init__(
        self,
        outcome_var: Union[str, SeriesSpecs, pd.Series],
        model_type: str,
        start_of_training_data: Union[str, datetime],
        end_of_test_data: Union[str, datetime],
        lags: List[int] = None,
        regressors: Union[List[str], List[SeriesSpecs], List[pd.Series]] = None,
        ratio_training_test_data=DEFAULT_RATIO_TRAINING_TEST_DATA,
        remodel_frequency: Union[str, timedelta] = DEFAULT_REMODELING_FREQUENCY,
        model_filename: str = None,
        creation_time: Union[str, datetime] = None,
        transform: transform_type = None,
    ):
        """Create a ModelSpecs instance. Accepts all parameters as string (besides transform - TODO) for
         deserialization support (JSON strings for all parameters which are not natively JSON-parseable,)"""
        self.outcome_var = parse_series_specs(outcome_var, "y")
        self.model_type = model_type
        self.lags = lags
        if self.lags is None:
            self.lags = []
        if regressors is None:
            self.regressors = []
        else:
            self.regressors = [
                parse_series_specs(r, "Regressor%d" % (regressors.index(r) + 1))
                for r in regressors
            ]
        if isinstance(start_of_training_data, str):
            self.start_of_training_data = dateutil.parser.parse(start_of_training_data)
        else:
            self.start_of_training_data = start_of_training_data
        if isinstance(end_of_test_data, str):
            self.end_of_test_data = dateutil.parser.parse(end_of_test_data)
        else:
            self.end_of_test_data = end_of_test_data
        self.ratio_training_test_data = ratio_training_test_data
        if isinstance(creation_time, str):
            self.creation_time = dateutil.parser.parse(creation_time)
        elif creation_time is None:
            self.creation_time = tz_aware_utc_now()
        else:
            self.creation_time = creation_time
        self.model_filename = model_filename
        if isinstance(remodel_frequency, str):
            self.remodel_frequency = timedelta(
                days=int(remodel_frequency) / 60 / 60 / 24
            )
        else:
            self.remodel_frequency = remodel_frequency
        self.transform = transform
        # TODO: load transform function. Not sure what is smart, maybe marshalling.

    def as_dict(self):
        return vars(self)

    def __repr__(self):
        return "ModelSpecs: <%s>" % pformat(vars(self))


def parse_series_specs(
    specs: Union[str, SeriesSpecs, pd.Series], name: str = None
) -> SeriesSpecs:
    if isinstance(specs, str):
        return load_series_specs_from_json(specs)
    elif isinstance(specs, pd.Series):
        return ObjectSeriesSpecs(specs, name)
    else:
        return specs


def load_series_specs_from_json(s: str) -> SeriesSpecs:
    json_repr = json.loads(s)
    series_class = globals()[json_repr["__series_type__"]]
    if series_class == ObjectSeriesSpecs:
        # load pd.Series from string, will be UTC-indexed, so apply original_tz
        json_repr["data"] = pd.read_json(
            json_repr["data"], typ="series", convert_dates=True
        )
        json_repr["data"].index = json_repr["data"].index.tz_localize(
            json_repr["original_tz"]
        )
    return series_class(
        **{k: v for k, v in json_repr.items() if not k.startswith("__")}
    )
