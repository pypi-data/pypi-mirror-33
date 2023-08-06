import typing

import networkx
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer

from sri.common import config
from sri.common import constants
from sri.common import util

Inputs = container.DataFrame  # container.List[networkx.Graph]
Outputs = container.DataFrame  # container.DataFrame[container.DataFrame]

class GraphToEdgeListHyperparams(meta_hyperparams.Hyperparams):
    include_edge_attributes = meta_hyperparams.Hyperparameter[bool](
            description = 'If true, any edge attributes will be include in the output.',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )

    include_node_attributes = meta_hyperparams.Hyperparameter[bool](
            description = 'If true, any node attributes will be include in the output. Node attributes will be included as a tuple of (source, target).',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )

class GraphToEdgeList(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphToEdgeListHyperparams]):
    """
    Convert graphs into edge lists (in the form of a DataFrame).
    Four columns will always be returned in the edge list: 'source', 'dest', 'directed', 'weight'.
    More columns may be returned based on the hyperparams.
    This is a inverse to the EdgeListToGraph primitive.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphToEdgeListHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        columns = ['source', 'dest', 'directed', 'weight']
        edge_list = container.DataFrame([], columns = columns)

        # TODO(eriq): Implement
        return pi_base.CallResult(container.DataFrame([edge_list], columns = ['edgelist']))

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '5f565b7a-9cb7-48c3-ae4d-84a57eb790af',
        'version': config.VERSION,
        'name': 'Graph to Edge List',
        'description': "Convert graphs into edge lists (in the form of a DataFrame). Four columns will always be returned in the edge list: 'source', 'dest', 'directed', 'weight'. More columns may be returned based on the hyperparams.",
        'python_path': 'd3m.primitives.data.GraphToEdgeList',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer' 'edge list' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
