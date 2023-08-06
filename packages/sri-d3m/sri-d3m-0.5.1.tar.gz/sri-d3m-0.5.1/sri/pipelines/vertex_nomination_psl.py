from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines.base import BasePipeline
from sri.graph.vertex_nomination import VertexNominationParser
from sri.psl.vertex_nomination import VertexNomination

DATASETS = {
    'DS01876',
    'LL1_net_nomination_seed',
}

class VertexNominationPSLPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = VertexNominationParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # TODO(eriq): Adjust output to use real targets. Need another primitive.

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = VertexNomination.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_argument(
                name = 'outputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Results', data_reference = 'steps.1.produce')

        return pipeline

    def assert_result(self, tester, results, dataset):
        tester.assertEquals(len(results), 1)
        # TODO(eriq); More
