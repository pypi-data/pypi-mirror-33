import os
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
from sri.graph.networkx import Graph
from sri.psl import hyperparams
from sri.psl import psl

# We can take just the annotated graph.
# TODO(eriq): How do we fix the size?
Inputs = container.List
Outputs = container.List

# TODO(eriq): Include all edges in targets? (param)
# TODO(eriq): Use the training data for weight learning?

PSL_MODEL = 'link_prediction'

class LinkPredictionHyperparams(hyperparams.PSLHyperparams):
    pass

class LinkPredictionParams(meta_params.Params):
    debug_options: typing.Dict

class LinkPrediction(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, LinkPredictionParams, LinkPredictionHyperparams]):
    """
    A primitive that performs link prediction on an annotated graph.

    Note: this is unsupervised because we take the dataset itself and set_training_data() does not want an output argument.
    """

    def __init__(self, *, hyperparams: LinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        annotatedGraph = self._validateInputs(inputs)
        result = self._link_prediction(annotatedGraph)

        outputs: container.List = container.List([result])
        metaInfo = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source=self)
        metadata = metadata.update((meta_base.ALL_ELEMENTS,), {'structural_type': int}, source = self)
        outputs.metadata = metadata

        return pi_base.CallResult(outputs)

    def _link_prediction(self, graph):
        self._write_psl_data(graph, self.hyperparams['psl_temp_dir'])
        pslOutput = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                int_args = True)

        return self._build_output_graph(pslOutput[constants.LINK_PREDICATE], graph)

    def _validateInputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Not exactly one input, found %d." % (len(inputs)))

        graph = inputs[0]

        if (not isinstance(graph, Graph)):
            raise ValueError("Expecting a graph, found a %s" % (type(graph).__name__))

        return graph

    def set_training_data(self, *, inputs: Inputs) -> None:
        # Weight learning not yet supported.
        pass

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def get_params(self) -> LinkPredictionParams:
        return LinkPredictionParams({
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: LinkPredictionParams) -> None:
        self._set_debug_options(params['debug_options'])

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    # PSL specific functionality.
    
    def _write_psl_data(self, graph, base_path, include_all_edges = False):
        """
        Decompose the graph into data for a PSL link prediction model.
        Every unobserved link (where a link exists, but has the property: 'observed': False) is a target.
        """
        self._logger.debug("Writing PSL data into '%s'", base_path)

        os.makedirs(base_path, exist_ok = True)

        self._write_predicate_graph(graph, os.path.join(base_path, constants.GRAPH1_PREDICATE_FILENAME), constants.NODE_MODIFIER_SOURCE)
        self._write_predicate_graph(graph, os.path.join(base_path, constants.GRAPH2_PREDICATE_FILENAME), constants.NODE_MODIFIER_TARGET)
        self._write_predicate_edge(graph, os.path.join(base_path, constants.EDGE1_PREDICATE_FILENAME), constants.NODE_MODIFIER_SOURCE)
        self._write_predicate_edge(graph, os.path.join(base_path, constants.EDGE2_PREDICATE_FILENAME), constants.NODE_MODIFIER_TARGET)
        self._write_predicate_link_prior(graph, os.path.join(base_path, constants.LINK_PRIOR_PREDICATE_FILENAME))
        self._write_predicate_link_observed(graph, os.path.join(base_path, constants.LINK_PREDICATE_OBS_FILENAME))

        if (include_all_edges):
            self._write_predicate_link_target_all(graph, os.path.join(base_path, constants.LINK_PREDICATE_TARGET_FILENAME))
        else:
            self._write_predicate_link_target(graph, os.path.join(base_path, constants.LINK_PREDICATE_TARGET_FILENAME))

        self._write_predicate_block(graph, os.path.join(base_path, constants.BLOCK_PREDICATE_FILENAME))

    # predicate_values should be {[atom arg, ...]: link value, ...}
    def _build_output_graph(self, predicate_values, in_graph):
        graph = Graph()

        for link in predicate_values:
            if (len(link) != 2):
                raise ValueError("Expecting links of length 2, got %s: (%s)." % (len(link), link))

            # TODO(eriq): Double check int/string consistency
            # source_id, target_id = str(link[0]), str(link[1])
            source_id, target_id = link[0], link[1]

            graph.add_node(source_id, **(in_graph.node[source_id]))
            graph.add_node(target_id, **(in_graph.node[target_id]))

            attributes = {
                constants.WEIGHT_KEY: predicate_values[link],
                constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                constants.INFERRED_KEY: True
            }
            graph.add_edge(source_id, target_id, **attributes)

        return graph

    def _write_predicate_graph(self, graph, path, graphId):
        rows = []

        for (id, data) in graph.nodes(data = True):
            if (data[constants.SOURCE_GRAPH_KEY] != graphId):
                continue
            rows.append([str(id)])

        util.write_tsv(path, rows)

    def _write_predicate_edge(self, graph, path, graphId):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip links.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_EDGE):
                continue

            # Skip edges that do not come from out target graph.
            if (graph.node[source][constants.SOURCE_GRAPH_KEY] != graphId):
                continue

            # Edges are undirected.
            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])
            rows.append([str(target), str(source), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_observed(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip links that are not observed.
            if (not data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_prior(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            # Since observed links are not targets, they have no prior.
            if (constants.OBSERVED_KEY in data and data[constants.OBSERVED_KEY]):
                continue

            if (constants.WEIGHT_KEY not in data):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_target(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            if (data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            # TODO(eriq): This should be unnecessary.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target)])

        util.write_tsv(path, rows)

    def _write_predicate_block(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            if (data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            # TODO(eriq): This should be unnecessary.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target)])

        util.write_tsv(path, rows)

    # Write every possible link that has not been observed.
    def _write_predicate_link_target_all(self, graph, path):
        for (id1, data1) in graph.nodes(data = True):
            if (data1[constants.SOURCE_GRAPH_KEY] != 1):
                continue

            for (id2, data2) in graph.nodes(data = True):
                if (data2[constants.SOURCE_GRAPH_KEY] != 2):
                    continue

                # Skip any observed links
                if (graph.has_edge(id1, id2) and graph[id1][id2][constants.OBSERVED_KEY]):
                    continue

                rows.append([str(id1), str(id2)])

        util.write_tsv(path, rows)







    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'd83aa8fe-0433-4462-be54-b4074959b6fc',
        'version': config.VERSION,
        'name': 'Link Prediction',
        'description': 'Perform collective link prediction.',
        'python_path': 'd3m.primitives.sri.psl.LinkPrediction',
        'primitive_family': meta_base.PrimitiveFamily.LINK_PREDICTION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'primitive', 'graph', 'link prediction', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
