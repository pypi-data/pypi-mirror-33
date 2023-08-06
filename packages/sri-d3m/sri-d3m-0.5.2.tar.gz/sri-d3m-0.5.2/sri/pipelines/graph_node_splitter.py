from d3m import container
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.graph.node_splitter import GraphNodeSplitter, GraphNodeSplitterHyperparams

# All graph datasets pass, some are left out for speed.
SKIP_DATASETS = {
    '6_70_com_amazon',
    '6_86_com_DBLP',
}
DATASETS = set(datasets.GRAPH_DATASETS) - SKIP_DATASETS

# TODO(eriq): This pipeline will not pass until we can set arguments. Maybe we need a wrapper primitive for testing?

class GraphNodeSplitterPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = GraphNodeSplitter.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.VALUE,
                # This will not work. Arguments have to be glued to other parts of the pipeline.
                data = container.List([1, 3]),
        )
        step_0.add_output('produce')
        step_0.add_output('produce_test')
        pipeline.add_step(step_0)

        pipeline.add_output(name = 'Train Splits', data_reference = 'steps.0.produce')
        pipeline.add_output(name = 'Test Splits', data_reference = 'steps.0.produce_test')

        return pipeline

    def assert_result(self, tester, results, dataset):
        num_fold = GraphNodeSplitterHyperparams.defaults()['num_fold']

        tester.assertEquals(len(results), 1)
        # TODO(eriq)
