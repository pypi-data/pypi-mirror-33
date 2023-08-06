import typing
import pandas

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised
from numpy import float64, int64, isnan
from common_primitives import utils

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame

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
        self._construct_dict()
        del(self.data)
        del(self.counts)
        del(self.total)
        return self

    def produce(self, data, colindex):

        def convert(x):
            try:
                x = self.converter(x)
                if isnan(x):
                    return self.median
                else:
                    return x
            except ValueError:
                return self.median

        # print("Converting column", col)
        data.iloc[:,colindex] = data.iloc[:,colindex].apply(convert)

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
        converted = {}
        first_total = 0
        for v in self.data:
            try:
                cv = self.converter(v)
                converted[v] = cv
                if not isnan(cv):
                    first_total += self.counts[v]
                    values.append(v)
            except ValueError:
                pass
        values = sorted(values, key=lambda x: converted[x])
        total = 0
        for v in values:
            total += self.counts[v]
            if total >= first_total * 0.5:
                self.median = converted[v]
                break

    def _construct_dict(self):
        pass

    def update_metadata(self, data, ci):
        pass

class CategoricalConditioner(ColumnConditioner):
    def can_handle(self):
        if not any(type(x) is str for x in self.data):
            return None
        if len(set(self.data)) > 20:
            return None
        return self

    def _calculate_median(self):
        pass

    def _construct_dict(self):
        keys = sorted(self.counts.keys(), reverse=True, key=lambda x: self.counts[x])
        self.dictionary = dict((keys[i], i+1) for i in range(len(keys)))
        
    def produce(self, data, colindex):
        def convert(x):
            try: 
                return self.dictionary[x]
            except:
                return 0
        data.iloc[:,colindex] = data.iloc[:,colindex].apply(convert).astype(int)

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = int
        data.metadata.update_column(ci, mdata)


class IntegerConditioner(ColumnConditioner):
    def __init__(self, col):
        super().__init__(col)
        self.converter = int

    def produce(self, data, colindex):
        super().produce(data, colindex)
        data.iloc[:,colindex] = data.iloc[:,colindex].astype(int)

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = int
        data.metadata.update_column(ci, mdata)

    def can_handle(self):
        dtype = self.data.dtype
        if dtype == float or dtype == float64:
            return None
        elif dtype == int or dtype == int64:
            return self
        else:
            return super().can_handle()

class FloatConditioner(ColumnConditioner):

    def __init__(self, col):
        super().__init__(col)
        self.converter = float

    def produce(self, data, colindex):
        super().produce(data, colindex)
        data.iloc[:,colindex] = data.iloc[:,colindex].astype(float)

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = float
        data.metadata.update_column(ci, mdata)

    def can_handle(self):
        dtype = self.data.dtype
        if dtype == float or dtype == float64:
            return self
        elif dtype == int or dtype == int64:
            return self
        else:
            return super().can_handle()

class NoOpConditioner(ColumnConditioner):

    def can_handle(self):
        return self

    def fit(self):
        return self

    def produce(self, data, colindex):
        pass

class ConditionerParams(meta_params.Params):
    column_conditioners: typing.Sequence[typing.Any]
    all_columns: typing.Set[str]
    width: int
    tossers: typing.Sequence[int]

class ConditionerHyperparams(meta_hyperparams.Hyperparams):
    ensure_numeric = meta_hyperparams.Hyperparameter[bool](
        default = False,
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class Conditioner(pi_unsupervised.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, ConditionerParams, ConditionerHyperparams]):
    def __init__(self, *, hyperparams: ConditionerHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

    def get_params(self) -> ConditionerParams:
        return ConditionerParams(column_conditioners=self._column_conditioners,
                                 all_columns=self._all_columns,
                                 width=self._width,
                                 tossers=self._tossers
        )

    def set_params(self, *, params: ConditionerParams) -> None:
        self._fitted = True
        self._all_columns = params['all_columns']
        self._width = params['width']
        self._column_conditioners : typing.List[typing.Any] = params['column_conditioners']
        self._tossers = params['tossers']

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_inputs = inputs
        self._fitted = False

    def fit(self, *, timeout:float = None, iterations: int = None) -> None:
        if self._fitted:
            return

        if self._training_inputs is None:
            raise ValueError('Missing training(fitting) data.')

        data_copy = self._data_copy = self._training_inputs.copy()
        self._all_columns = set(data_copy.columns)
        self._width = len(data_copy.columns)
        # self._column_conditioners = dict((c.name, self._fit_column(c)) for c in data_copy.columns)
        self._column_conditioners : typing.List[typing.Any] = []
        for i,c in enumerate(data_copy.columns):
            self._column_conditioners.append(self._fit_column(i))

        self._tossers = []
        if self.hyperparams['ensure_numeric']:
            self._tossers = list(reversed([i for i in range(self._width)
                                           if isinstance(self._column_conditioners[i], NoOpConditioner)]))

        # print("Fitted col conditioners: %d" % len(self._column_conditioners))

        self._fitted = True

    def _fit_column(self, colindex):
        col = self._data_copy.iloc[:, colindex]
        for cls in (IntegerConditioner, FloatConditioner, CategoricalConditioner, NoOpConditioner):
            obj = cls(col).can_handle()
            if obj is not None:
                obj.fit()
                # print(colname, cls)
                return obj

    def produce(self, *, inputs: Inputs, timeout:float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        if isinstance(inputs, container.DataFrame) or isinstance(inputs, pandas.DataFrame):
            data_copy = inputs.copy()
        else:
            data_copy = inputs[0].copy()

        set_columns = set(data_copy.columns)
        width = len(data_copy.columns)

        if set_columns != self._all_columns or width != self._width:
            raise ValueError('Columns(features) fed at produce() differ from fitted data.')

        for i,col in enumerate(data_copy.columns):
            # print("Produce %d" % i)
            self._column_conditioners[i].produce(data_copy, i)
            self._column_conditioners[i].update_metadata(data_copy, i)

        # We don't want to retain any of the columns we don't know how to handle
        if self.hyperparams['ensure_numeric']:
            for i in self._tossers:
                data_copy = utils.remove_column(data_copy, i)

        return pi_base.CallResult(data_copy)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        "id": "6fdcf530-2cfe-4e87-9d9e-b8770753e19c",
        "version": config.VERSION,
        "name": "Autoflow Data Conditioner",
        "description": "Perform robust type inference and imputation.",
        "python_path": "d3m.primitives.sri.autoflow.Conditioner",
        "primitive_family": meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        "algorithm_types": [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset', 'transformer' ],
        'installation': [ config.INSTALLATION ],
    })
