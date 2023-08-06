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

Inputs = container.Dataset
Outputs = container.DataFrame

class MeanBaselineHyperparams(meta_hyperparams.Hyperparams):
    pass

class MeanBaselineParams(meta_params.Params):
    pass

class MeanBaseline(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, MeanBaselineParams, MeanBaselineHyperparams]):
    """
    A simple baseline that just predicts the mean/plurality.
    This is not meant to be used in production, just a way to get quick and reasonable answers for debugging.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: MeanBaselineHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = get_logger(__name__)
        self._targetName = None
        self._targetDataElement = None
        self._prediction = None

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs) -> None:
        labels, average, targetName, targetDataElement = self._validate_training_input(inputs)
        self._targetName = targetName
        self._targetDataElement = targetDataElement
        self._prediction = self._process_data(labels, average)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        ids = self._validate_test_input(inputs)
        predictions = [self._prediction for id in ids]

        # TODO(eriq): Just make a frame with all the ids x prediction.
        result = container.DataFrame(data = {'d3mIndex': ids, self._targetName: predictions})

        self._logger.debug("Produce complete")

        return pi_base.CallResult(result)

    def get_params(self) -> MeanBaselineParams:
        return MeanBaselineParams()

    def set_params(self, *, params: MeanBaselineParams) -> None:
        pass

    def _validate_training_input(self, inputs: Inputs):
        targetDataElement = None
        targetColumn = None
        average = False

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

                targetDataElement = dataElement
                targetColumn = columnInfo['name']
                average = ('http://schema.org/Float' in columnInfo['semantic_types'])
                break

            if (targetColumn is not None):
                break

        if (targetColumn is None):
            raise ValueError("Could not figure out target column.")

        labels = list(inputs[dataElement][targetColumn])

        if (average):
            labels = [float(value) for value in labels]

        return labels, average, targetColumn, targetDataElement

    # Just get the d3mIndexes
    def _validate_test_input(self, inputs: Inputs):
        return list(inputs[self._targetDataElement]['d3mIndex'])

    def _process_data(self, labels, average):
        self._logger.debug("Processing data")

        predicatedValue = None
        if (average):
            predicatedValue = self._calcMean(labels)
        else:
            predicatedValue = self._calcPlurality(labels)

        self._logger.debug("Data processing complete")

        return predicatedValue

    def _calcMean(self, labels):
        mean = 0.0
        for label in labels:
            mean += label
        mean /= len(labels)

        return mean

    def _calcPlurality(self, labels):
        counts = {}

        for label in labels:
            if (label not in counts):
                counts[label] = 0
            counts[label] += 1

        bestCount = 0
        bestLabel = None

        for (label, count) in counts.items():
            if (count > bestCount):
                bestCount = count
                bestLabel = label

        return bestLabel

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '36d5472c-e0a4-4ed6-a1d0-2665feacff39',
        'version': config.VERSION,
        'name': 'Mean Baseline',
        'description': 'A baseline primitive that just predicate the mean/plurality. Not indented for production, only debugging.',
        'python_path': 'd3m.primitives.sri.baseline.MeanBaseline',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
