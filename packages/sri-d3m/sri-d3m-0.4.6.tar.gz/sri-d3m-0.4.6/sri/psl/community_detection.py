import typing

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

PSL_MODEL = 'community_detection'

# TODO(eriq): Implement.

class CommunityDetectionHyperparams(hyperparams.PSLHyperparams):
    pass

class CommunityDetectionParams(meta_params.Params):
    debug_options: typing.Dict

class CommunityDetection(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, CommunityDetectionParams, CommunityDetectionHyperparams]):
    """
    Solve community detection with PSL.
    """

    def __init__(self, *, hyperparams: CommunityDetectionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        pass

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        output = container.DataFrame([])
        return pi_base.CallResult(output)

    def get_params(self) -> CommunityDetectionParams:
        return CommunityDetectionParams({
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: CommunityDetectionParams) -> None:
        self._set_debug_options(params['debug_options'])

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '5b08a46a-28f6-4987-a8c6-840edd5877b0',
        'version': config.VERSION,
        'name': 'Community Detection',
        'description': 'Solve community detection using PSL.',
        'python_path': 'd3m.primitives.sri.psl.CommunityDetection',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            # TODO(eriq): Change once we our MRF addition comes into the main release.
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'primitive', 'relational', 'general', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_NESTED_VALUES ],
        'effects': [
            meta_base.PrimitiveEffects.NO_MISSING_VALUES,
            meta_base.PrimitiveEffects.NO_NESTED_VALUES
        ],
        'hyperparms_to_tune': [
        ]
    })
