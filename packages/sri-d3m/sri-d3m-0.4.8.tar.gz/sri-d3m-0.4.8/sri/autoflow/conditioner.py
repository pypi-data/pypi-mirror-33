import typing
import pandas

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame

class ConditionerParams(meta_params.Params):
    column_conditioners: typing.Dict
    all_columns: typing.Set[str]

class ConditionerHyperparams(meta_hyperparams.Hyperparams):
    pass

class ColumnConditioner(object):
    def __init__(self, col):
        self.data = col

    def can_handle(self):
        clen = len(self.data)
        if clen == 0:
            return None
        failures = 0
        for x in self.data:
            try:
                self.converter(x)
            except ValueError:
                failures += 1
                if float(failures) / clen > 0.5:
                    return None
        return self

    def fit(self):
        self._tally()
        self._calculate_median()
        del(self.data)
        del(self.counts)
        del(self.total)
        return self

    def produce(self, data, col):

        def convert(x):
            try:
                return self.converter(x)
            except ValueError:
                return self.median

#        print("Converting column", col)
        data[col] = data[col].apply(convert)

    def _tally(self):
        self.counts = {}
        self.total = 0
        for x in self.data:
            self.total += 1
            try:
                self.counts[x] += 1
            except KeyError:
                self.counts[x] = 1

    def _calculate_median(self):
        values = []
        for v in self.data:
            try:
                self.converter(v)
                values.append(v)
            except ValueError:
                pass
        values = sorted(values, key=lambda x: self.converter(x))
        total = 0
        for v in values:
            total += self.counts[v]
            if total >= self.total * 0.5:
                self.median = self.converter(v)
                break


class IntegerConditioner(ColumnConditioner):

    def __init__(self, col):
        super().__init__(col)
        self.converter = int

    def produce(self, data, col):
        super().produce(data, col)
        data[col] = data[col].astype(int)


class FloatConditioner(ColumnConditioner):

    def __init__(self, col):
        super().__init__(col)
        self.converter = float

    def produce(self, data, col):
        super().produce(data, col)
        data[col] = data[col].astype(float)


class NoOpConditioner(ColumnConditioner):

    def can_handle(self):
        return self

    def fit(self):
        return self

    def produce(self, data, col):
        return col


class Conditioner(pi_unsupervised.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, ConditionerParams, ConditionerHyperparams]):

    def get_params(self) -> ConditionerParams:
        return ConditionerParams(column_conditioners=self._column_conditioners,
                      all_columns=self._all_columns)

    def set_params(self, *, params: ConditionerParams) -> None:
        self._fitted = True
        self._all_columns = params['all_columns']
        self._column_conditioners = params['column_conditioners']

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_inputs = inputs
        self._fitted = False

    def fit(self, *, timeout:float = None, iterations: int = None) -> None:
        """
        Need training data from set_training_data first.
        The encoder would record categorical columns identified and
        the corresponding (with top n occurrence) column values to
        one-hot encode later in the produce step.
        """
        if self._fitted:
            return

        if self._training_inputs is None:
            raise ValueError('Missing training(fitting) data.')

        data_copy = self._data_copy = self._training_inputs.copy()
        self._all_columns = set(data_copy.columns)
#        self._column_conditioners = dict((c.name, self._fit_column(c))
#                                         for c in data_copy.columns)
        self._column_conditioners = {}
        for c in data_copy:
            self._column_conditioners[c] = self._fit_column(c)

        self._fitted = True

    def _fit_column(self, colname):
        col = self._data_copy[colname]
        for cls in (IntegerConditioner, FloatConditioner, NoOpConditioner):
            cond = cls(col).can_handle()
            if cond is not None:
                cond.fit()
#                print(colname, cls)
                return cond

    def produce(self, *, inputs: Inputs, timeout:float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        """
        Convert and output the input data into encoded format,
        using the trained (fitted) encoder.
        Notice that [colname]_other_ and [colname]_nan columns
        are always kept for one-hot encoded columns.
        """

        if isinstance(inputs, container.DataFrame) or isinstance(inputs, pandas.DataFrame):
            data_copy = inputs.copy()
        else:
            data_copy = inputs[0].copy()

        set_columns = set(data_copy.columns)

        if set_columns != self._all_columns:
            raise ValueError('Columns(features) fed at produce() differ from fitted data.')

        for col in data_copy:
            self._column_conditioners[col].produce(data_copy, col)

        return pi_base.CallResult(data_copy)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        "id": "6fdcf530-2cfe-4e87-9d9e-b8770753e19c",
        "version": config.VERSION,
        "name": "Autoflow Data Conditioner",
        "description": "Perform simple type inference and data imputation.",
        "python_path": "d3m.primitives.sri.autoflow.Conditioner",
        "primitive_family": meta_base.PrimitiveFamily.DATA_CLEANING,
        "algorithm_types": [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset', 'transformer', 'unsupervised_learning' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_NESTED_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES, meta_base.PrimitiveEffects.NO_NESTED_VALUES ],
        'hyperparms_to_tune': []
    })
