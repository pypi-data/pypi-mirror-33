import os
import tempfile
import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised_learning

from sri.common import config

# A list of test folds.
Inputs = container.List  # container.List[int]
Outputs = container.List  # container.List[container.Dataset]

class GraphNodeSplitterHyperparams(meta_hyperparams.Hyperparams):
    num_fold = meta_hyperparams.Bounded(
            description = 'The number of folds in k-fold cross-validation.',
            default = 10,
            lower = 0,
            upper = None,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )
    delete_recursive = meta_hyperparams.Hyperparameter[bool](
            default = True,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'Ignored for graph sampling.',
    )
    stratified = meta_hyperparams.Hyperparameter[bool](
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'Ignored for graph sampling.',
    )
    file_output_path = meta_hyperparams.Hyperparameter[str](
            default = os.path.abspath(os.path.join(tempfile.gettempdir(), 'graph_node_splitter')),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'A place on disk were we can store the split graphs.',
    )

class GraphNodeSplitter(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, None, GraphNodeSplitterHyperparams]):
    """
    Take in a graph-based dataset and produce multiple train/test splits over the graph.
    This is achieved by sampling nodes in the graph.
    The output will be a DataFrame with two columns: "train" and "test", each containing a full container.Dataset.
    Each row will be one of these train/test splits.,
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphNodeSplitterHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

    def set_training_data(self, *, inputs: Inputs) -> None:
        # TODO(eriq): Remoce once TestPrimitive is in core:
        # https://gitlab.com/datadrivendiscovery/common-primitives/merge_requests/11/diffs
        pass

    def _set_training_data(self, *, dataset: container.Dataset) -> None:
        # TODO(eriq): Change the name once TestPrimitive is in core:
        # https://gitlab.com/datadrivendiscovery/common-primitives/merge_requests/11/diffs
        pass

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        """
        Compute the folds.
        """

        # TODO(eriq): Compute
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        """
        Produce the training splits from the provided test fold specifications.

        Returns
        -------
        List[Dataset]
            A list of dataset where each dataset is a train dataset obtained from all the folds minus the given test fold.
            For example, if we have num_fold = 5 and [1, 3] is specified, then [Dataset(2, 3, 4, 5) and Dataset(1, 2, 4, 5)]
            will be produced.
        """

        # TODO(eriq): Get the train folds.
        results = container.List([None] * len(inputs))
        return pi_base.CallResult(results)

    def produce_test(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        """
        Produce the test splits from the provided test fold specifications.

        Returns
        -------
        List[Dataset]
            A list of dataset where each dataset is a test dataset obtained from the given test fold.
            For example, if we have num_fold = 5 and [1, 3] is specified, then [Dataset(1) and Dataset(3)]
            will be produced.
        """

        # TODO(eriq): Get the test folds.
        results = container.List([None] * len(inputs))
        return pi_base.CallResult(results)

    def get_params(self) -> None:
        return None

    def set_params(self, *, params: None) -> None:
        return None

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '0a934c8d-610f-44ab-9c44-6ced17194d4c',
        'version': config.VERSION,
        'name': 'Mean Baseline',
        'description': 'Take in a graph-based dataset and produce multiple train/test splits over the graph. This is achieved by sampling nodes in the graph.',
        'python_path': 'd3m.primitives.data.GraphNodeSplitter',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'dataset', 'graph', 'sampling', 'evaluation' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'hyperparms_to_tune': []
    })
