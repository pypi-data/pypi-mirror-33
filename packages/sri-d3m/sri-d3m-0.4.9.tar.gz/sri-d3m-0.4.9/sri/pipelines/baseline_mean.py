from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.baseline.mean import MeanBaseline
from sri.pipelines.base import BasePipeline

# All datasets pass, some are left out for speed.
SKIP_DATASETS = {
    '31_urbansound',
    '6_70_com_amazon',
    '6_86_com_DBLP',
    'uu3_world_development_indicators',
}
DATASETS = set(datasets.get_dataset_names()) - SKIP_DATASETS

class MeanBaselinePipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = MeanBaseline.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'results', data_reference = 'steps.0.produce')

        return pipeline

    def assert_result(self, tester, results, dataset):
        # The results are always nested.
        tester.assertEquals(len(results), 1)
        tester.assertEquals(len(results[0]), datasets.get_count(dataset))
