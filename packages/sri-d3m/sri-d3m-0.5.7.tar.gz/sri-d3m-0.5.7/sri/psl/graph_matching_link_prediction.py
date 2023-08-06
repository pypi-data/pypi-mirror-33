import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised_learning

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.graph.graph_matching import GraphMatchingParser
from sri.graph.graph_matching import GraphMatchingParserHyperparams
from sri.graph.transform import GraphTransformerHyperparams
from sri.graph.transform import GraphTransformer
from sri.graph.networkx import Graph
from sri.psl.link_prediction import LinkPrediction
from sri.psl.link_prediction import LinkPredictionHyperparams

# The test data will just look like a dataset, but the match column will be empty.
Inputs = container.Dataset
# Return match or no match.
Outputs = container.DataFrame

class GraphMatchingLinkPredictionHyperparams(meta_hyperparams.Hyperparams):
    truth_threshold = meta_hyperparams.Hyperparameter[float](
            default = 0.50,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    graph_matching_parser_hyperparams = meta_hyperparams.Hyperparameter(
            default = GraphMatchingParserHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    graph_transform_hyperparams = meta_hyperparams.Hyperparameter(
            default = GraphTransformerHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    link_prediction_hyperparams = meta_hyperparams.Hyperparameter(
            default = LinkPredictionHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

# TODO(eriq): LinkPrediction currently doesn't carry any state, but it will some day.
class GraphMatchingLinkPredictionParams(meta_params.Params):
    training_set: Inputs
    debug_options: typing.Dict

class GraphMatchingLinkPrediction(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, GraphMatchingLinkPredictionParams, GraphMatchingLinkPredictionHyperparams]):
    """
    A primitive that takes a graph matching problem and does full link prediction on it.
    This just strings together various other primitives.

    Note: this is unsupervised because we take the dataset itself and set_training_data() does not want an output argument.
    """

    def __init__(self, *, hyperparams: GraphMatchingLinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._gm_parser = GraphMatchingParser(
                hyperparams = self.hyperparams['graph_matching_parser_hyperparams'],
                _debug_options = _debug_options)

        self._transformer = GraphTransformer(
                hyperparams = self.hyperparams['graph_transform_hyperparams'],
                _debug_options = _debug_options)

        self._link_prediction = LinkPrediction(
                hyperparams = self.hyperparams['link_prediction_hyperparams'],
                _debug_options = _debug_options)

        self._training_dataset = None
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        self._gm_parser._set_debug_options(_debug_options)
        self._transformer._set_debug_options(_debug_options)
        self._link_prediction._set_debug_options(_debug_options)

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_dataset = inputs

        # See produce() about this.
        # self._link_prediction.set_training_data(inputs = self._full_transform(inputs), outputs = None)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # See produce() about this.
        # return self._link_prediction.fit(timeout = timeout, iterations = iterations)
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        input_graph = self._full_transform(self._training_dataset, inputs)
        # Normally, we would use the training graph for weight learning and this one for inference.
        # However, the data is split incorrectly.
        # So instead, we will run inference on the training graph and just grab the desired edges from the test dataset.
        output_graph = self._link_prediction.produce(inputs = input_graph, timeout = timeout, iterations = iterations).value[0]

        outputs: container.DataFrame = self._get_target_links(inputs, output_graph)

        return pi_base.CallResult(outputs)

    def get_params(self) -> GraphMatchingLinkPredictionParams:
        return GraphMatchingLinkPredictionParams({
            'training_set': self._training_dataset,
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: GraphMatchingLinkPredictionParams) -> None:
        self._training_dataset = params['training_set']
        self._set_debug_options(params['debug_options'])

    # Take in a dataset and turn it into a graph for link prediction.
    def _full_transform(self, dataset: Inputs, test_dataset: Inputs) -> container.List:
        parsed_graphs = self._gm_parser.produce(inputs = dataset).value

        # Because the test data is split incorrectly,
        # we have to merge the train and test data together.
        link_graph = parsed_graphs[2]
        for row in test_dataset[constants.GRAPH_MATCHING_DATASET_TABLE_INDEX].itertuples():
            source_node_id = int(row[2])
            target_node_id = int(row[3])

            source_label = util.computeNodeLabel(source_node_id, constants.NODE_MODIFIER_SOURCE)
            target_label = util.computeNodeLabel(target_node_id, constants.NODE_MODIFIER_TARGET)

            if (not link_graph.has_node(source_label)):
                attributes = {
                    constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_SOURCE,
                    constants.NODE_ID_LABEL: source_node_id,
                }
                link_graph.add_node(source_label, **attributes)

            if (not link_graph.has_node(target_label)):
                attributes = {
                    constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_TARGET,
                    constants.NODE_ID_LABEL: target_node_id,
                }
                link_graph.add_node(target_label, **attributes)

            if (not link_graph.has_edge(source_label, target_label)):
                attributes = {
                    constants.WEIGHT_KEY: -1,
                    constants.TARGET_KEY: True
                }
                link_graph.add_edge(source_label, target_label, **attributes)

        return self._transformer.produce(inputs = parsed_graphs).value

    # Use the input dataset and output graph to get the values for the desired links.
    def _get_target_links(self, dataset: Inputs, output_graph: Graph) -> container.DataFrame:
        d3m_indexes = []
        matches = []

        true_links = self._get_true_links(output_graph)

        for row in dataset[constants.GRAPH_MATCHING_DATASET_TABLE_INDEX].itertuples():
            d3m_index = int(row[1])
            source_node_id = int(row[2])
            target_node_id = int(row[3])

            source_label = util.computeNodeLabel(source_node_id, constants.NODE_MODIFIER_SOURCE)
            target_label = util.computeNodeLabel(target_node_id, constants.NODE_MODIFIER_TARGET)

            d3m_indexes.append(d3m_index)
            if ((source_label, target_label) in true_links):
                matches.append(1)
            else:
                matches.append(0)

        return container.DataFrame(data = {'d3mIndex': d3m_indexes, 'match': matches})

    # Returns: {(source label, target label): True, ...}
    def _get_true_links(self, graph: Graph) -> typing.Dict:
        links = {}

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            if (data[constants.WEIGHT_KEY] >= self.hyperparams['truth_threshold']):
                links[(source, target)] = True

        return links

    # Returns: {source label: (best target label, best target value), ...}.
    def _get_best_links(self, graph: Graph) -> typing.Dict:
        links = {}

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            if (source not in links or links[source][1] < data[constants.WEIGHT_KEY]):
                links[source] = (target, data[constants.WEIGHT_KEY])

        return links

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '2d782d55-f7ac-4abe-b228-39afcda1bbb3',
        'version': config.VERSION,
        'name': 'Graph Matching Link Prediction',
        'description': 'Give a full solution to "graph matching"-like problems using collective link prediction.',
        'python_path': 'd3m.primitives.sri.psl.GraphMatchingLinkPrediction',
        'primitive_family': meta_base.PrimitiveFamily.LINK_PREDICTION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'link prediction', 'collective classifiction'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
