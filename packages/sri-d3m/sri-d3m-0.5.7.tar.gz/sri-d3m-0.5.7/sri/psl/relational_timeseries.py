import os
import typing

import pandas
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import supervised_learning as pi_supervised_learning

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.psl import hyperparams
from sri.psl import psl

Inputs = container.DataFrame
Outputs = container.DataFrame

PSL_MODEL = 'relational_timeseries'

NEXT_TIME_FILENAME = 'next_time_obs.txt'
NEXT_PERIOD_FILENAME = 'next_period_obs.txt'
PRIOR_FILENAME = 'prior_obs.txt'

VALUE_OBS_FILENAME = 'value_obs.txt'
VALUE_TARGET_FILENAME = 'value_target.txt'

# TODO(eriq): Right now we only support a single period, but often timeseries show multiple.
# TODO(eriq): Learn weights.

class RelationalTimeseriesHyperparams(hyperparams.PSLHyperparams):
    period = meta_hyperparams.Hyperparameter[int](
            default = 7,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    time_indicator_column = meta_hyperparams.Hyperparameter[str](
            default = constants.D3M_INDEX,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class RelationalTimeseriesParams(meta_params.Params):
    debug_options: typing.Dict

class RelationalTimeseries(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, RelationalTimeseriesParams, RelationalTimeseriesHyperparams]):
    """
    A primitive that looks at a timeseries as a Markov model.
    """

    def __init__(self, *, hyperparams: RelationalTimeseriesHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

        self._prediction_column = None
        self._mean_prediction = None
        self._min_prediction = None
        self._max_prediction = None
        self._training_data = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # There should be two columns, and we don't want the d3m index.
        prediction_index = (1 + outputs.columns.get_loc(constants.D3M_INDEX)) % 2
        self._prediction_column = outputs.columns[prediction_index]

        predictions = pandas.to_numeric(outputs[self._prediction_column])

        # self._mean_prediction = float(predictions.mean())
        self._mean_prediction = float(predictions.median())

        self._min_prediction = float(predictions.min())
        self._max_prediction = float(predictions.max())

        train_data = inputs.merge(outputs, on = constants.D3M_INDEX, how = 'inner', suffixes = ('', '_output'))
        self._training_data = train_data[[self.hyperparams['time_indicator_column'], self._prediction_column]]

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        # First select out only the data we need.
        inputs = inputs[[constants.D3M_INDEX, self.hyperparams['time_indicator_column']]]

        self._write_data(inputs)
        psl_output = self._run_psl()
        output = self._build_output(inputs, psl_output)

        return pi_base.CallResult(output)

    def _write_data(self, targets):
        os.makedirs(self.hyperparams['psl_temp_dir'], exist_ok = True)

        time_col = self.hyperparams['time_indicator_column']

        times = set(pandas.to_numeric(self._training_data[time_col]))
        times |= set(pandas.to_numeric(targets[time_col]))
        times = sorted(list(times))

        next_times = [(time, time + 1) for time in times]
        next_period = [(time, time + self.hyperparams['period']) for time in times]
        prior = [(0, self._normalize_value(self._mean_prediction))]

        value_obs = []
        for (index, row) in self._training_data.iterrows():
            value_obs.append((row[time_col], self._normalize_value(row[self._prediction_column])))

        value_target = [(row[time_col],) for (index, row) in targets.iterrows()]
        
        path = os.path.join(self.hyperparams['psl_temp_dir'], NEXT_TIME_FILENAME)
        util.write_tsv(path, next_times)
        
        path = os.path.join(self.hyperparams['psl_temp_dir'], NEXT_PERIOD_FILENAME)
        util.write_tsv(path, next_period)
        
        path = os.path.join(self.hyperparams['psl_temp_dir'], PRIOR_FILENAME)
        util.write_tsv(path, prior)
        
        path = os.path.join(self.hyperparams['psl_temp_dir'], VALUE_OBS_FILENAME)
        util.write_tsv(path, value_obs)

        path = os.path.join(self.hyperparams['psl_temp_dir'], VALUE_TARGET_FILENAME)
        util.write_tsv(path, value_target)

    def _normalize_value(self, value):
        return (float(value) - self._min_prediction) / (self._max_prediction - self._min_prediction)

    def _denormalize_value(self, value):
        return float(value) * (self._max_prediction - self._min_prediction) + self._min_prediction

    def _run_psl(self):
        psl_output = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                lazy = True)

        # We only care about the Value predicate.
        psl_output = psl_output['VALUE']

        for args in psl_output:
            psl_output[args] = self._denormalize_value(psl_output[args])

        return psl_output

    def _build_output(self, inputs, psl_output):
        # Build up the result.
        output = []

        for (index, row) in inputs.iterrows():
            d3mIndex = row[constants.D3M_INDEX]
            # TODO(eriq): This may not always be safe.
            time = int(row[self.hyperparams['time_indicator_column']])

            prediction = self._mean_prediction
            if ((time,) in psl_output):
                prediction = psl_output[(time,)]

            output.append([d3mIndex, prediction])

        return container.DataFrame(output, columns = [constants.D3M_INDEX, self.hyperparams['time_indicator_column']])

    def get_params(self) -> RelationalTimeseriesParams:
        return RelationalTimeseriesParams({
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: RelationalTimeseriesParams) -> None:
        self._set_debug_options(params['debug_options'])

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '03b1288c-d4f5-4fa8-9a49-32e82c5efaf2',
        'version': config.VERSION,
        'name': 'Relational Timeseries',
        'description': 'Perform collective timeseries prediction.',
        'python_path': 'd3m.primitives.sri.psl.RelationalTimeseries',
        'primitive_family': meta_base.PrimitiveFamily.TIME_SERIES_FORECASTING,
        'algorithm_types': [
            # TODO(eriq): Change once we our MRF addition comes into the main release.
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'primitive', 'relational', 'timeseries', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_NESTED_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES, meta_base.PrimitiveEffects.NO_NESTED_VALUES ],
        # TODO(eriq)
        'hyperparms_to_tune': []
    })
