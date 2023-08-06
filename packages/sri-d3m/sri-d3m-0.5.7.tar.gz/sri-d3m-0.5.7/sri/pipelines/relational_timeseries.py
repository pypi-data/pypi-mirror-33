from d3m.metadata import pipeline as meta_pipeline
from d3m.primitives.datasets import DatasetToDataFrame
from d3m.primitives.data import ExtractColumnsBySemanticTypes

from sri.pipelines.base import BasePipeline
from sri.psl.relational_timeseries import RelationalTimeseries

DATASETS = {
    '56_sunspots',
}

class RelationalTimeseriesPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = DatasetToDataFrame.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = ExtractColumnsBySemanticTypes.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_hyperparameter(
                name = 'semantic_types',
                argument_type = meta_pipeline.ArgumentType.VALUE,
                data = ['https://metadata.datadrivendiscovery.org/types/Attribute']
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        step_2 = meta_pipeline.PrimitiveStep(primitive_description = ExtractColumnsBySemanticTypes.metadata.query())
        step_2.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_2.add_hyperparameter(
                name = 'semantic_types',
                argument_type = meta_pipeline.ArgumentType.VALUE,
                data = ['https://metadata.datadrivendiscovery.org/types/SuggestedTarget']
        )
        step_2.add_output('produce')
        pipeline.add_step(step_2)

        step_3 = meta_pipeline.PrimitiveStep(primitive_description = RelationalTimeseries.metadata.query())
        step_3.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.1.produce'
        )
        step_3.add_argument(
                name = 'outputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.2.produce'
        )
        step_3.add_output('produce')
        pipeline.add_step(step_3)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Results', data_reference = 'steps.3.produce')

        return pipeline

    def assert_result(self, tester, results, dataset):
        tester.assertEquals(len(results), 1)
        # TODO(eriq); More
