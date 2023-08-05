import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer

from sri.common import config
from sri.common import constants
from sri.common import util

Inputs = container.Dataset
Outputs = container.DataFrame

class LinkPredictionParserHyperparams(meta_hyperparams.Hyperparams):
    pass

class LinkPredictionParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, LinkPredictionParserHyperparams]):
    """
    Pull all the graph data out of a 'link prediction' style problem.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: LinkPredictionParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        # TODO(eriq): Implement
        return pi_base.CallResult(container.DataFrame([]))

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '5135ddb4-166b-45f4-b7bc-4b4674ccb3ef',
        'version': config.VERSION,
        'name': 'Link Prediction Parser',
        'description': 'Transform "link prediction"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.sri.graph.LinkPredictionParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
