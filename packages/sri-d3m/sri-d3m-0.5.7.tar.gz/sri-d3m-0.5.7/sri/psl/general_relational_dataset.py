import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised_learning

from sri.common import config
from sri.common import constants
from sri.common.util import get_logger
from sri.common.util import set_logging_level
from sri.psl.general_relational import GeneralRelational, GeneralRelationalHyperparams, GeneralRelationalParams

Inputs = container.Dataset
Outputs = container.DataFrame

# TODO(eriq): Support the pre-processing in another primitive and
# expose GeneralRelational as an entrypoint.

# Note the usage or GeneralRelational params/hyperparams
class GeneralRelationalDataset(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, GeneralRelationalParams, GeneralRelationalHyperparams]):
    """
    An extension to the GeneralRelational primitive that deals with a dataset as input.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GeneralRelationalHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = get_logger(__name__)
        self._set_debug_options(_debug_options)

        self._target_data_element = None
        self._target_column = None
        self._categorical = None
        self._primitive = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._validate_training_input(inputs)

        train_input = inputs[self._target_data_element].drop(columns = [self._target_column])
        train_output = inputs[self._target_data_element][[constants.D3M_INDEX, self._target_column]]

        defaults = GeneralRelationalHyperparams.defaults()
        hyperparams = GeneralRelationalHyperparams(defaults, categorical = self._categorical)
        self._primitive = GeneralRelational(
                hyperparams = hyperparams,
                _debug_options = self._debug_options)

        self._primitive.set_training_data(inputs = train_input, outputs = train_output)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        self._primitive.fit()
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        test_input = inputs[self._target_data_element].drop(columns = [self._target_column])
        output = self._primitive.produce(inputs = test_input, timeout = timeout, iterations = iterations)

        self._logger.debug("Produce complete")

        return output

    def get_params(self) -> GeneralRelationalParams:
        return GeneralRelationalParams()

    def set_params(self, *, params: GeneralRelationalParams) -> None:
        pass

    def _validate_training_input(self, inputs: Inputs):
        numDataElements = int(inputs.metadata.query([])['dimension']['length'])

        for dataElementRaw in range(numDataElements):
            dataElement = "%d" % (dataElementRaw)

            # Skip types without columns.
            if ('https://metadata.datadrivendiscovery.org/types/Graph' in inputs.metadata.query((dataElement,))['semantic_types']):
                continue

            numCols = int(inputs.metadata.query((dataElement, meta_base.ALL_ELEMENTS))['dimension']['length'])

            for i in range(numCols):
                columnInfo = inputs.metadata.query((dataElement, meta_base.ALL_ELEMENTS, i))

                if ('https://metadata.datadrivendiscovery.org/types/SuggestedTarget' not in columnInfo['semantic_types']):
                    continue

                self._target_data_element = dataElement
                self._target_column = columnInfo['name']

                self._categorical = False
                if ('https://metadata.datadrivendiscovery.org/types/CategoricalData' in columnInfo['semantic_types']):
                    self._categorical = True

                return

        raise ValueError("Could not figure out target column.")

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '4d989759-affd-4a51-a4e6-1a05a5c1d1c8',
        'version': config.VERSION,
        'name': 'General Relational Dataset',
        'description': 'Invoke the General Relational primitive on any dataset. Although preparing the dataset can be done by several common primtives, the spirit of this primtive is to work on all datasets without dependencies.',
        'python_path': 'd3m.primitives.sri.psl.GeneralRelationalDataset',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'primitive', 'relational', 'general', 'collective classifiction', 'dataset' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [
            meta_base.PrimitiveEffects.NO_MISSING_VALUES,
            meta_base.PrimitiveEffects.NO_NESTED_VALUES
        ],
        'hyperparms_to_tune': []
    })
