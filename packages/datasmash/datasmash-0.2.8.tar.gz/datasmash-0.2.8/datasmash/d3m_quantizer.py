import time
import os
import shutil
import pandas.api.types as ptypes # can use?
from typing import Dict
from sklearn.ensemble import RandomForestClassifier
from datasmash.quantizer import Quantizer, vectorize_label
from datasmash.utils import xgenesess, argmax_prod_matrix_list, pprint_dict
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.config import CWD, BIN_PATH
from datasmash._version import __version__
from d3m import container, utils as d3m_utils
#from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from d3m.metadata import hyperparams, params, base
from d3m.container import dataset, numpy, pandas
from d3m.primitive_interfaces.base import CallResult, DockerContainer
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase


Inputs = container.DataFrame
Outputs = container.DataFrame


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass


class d3m_Quantizer(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """

    """
    __author__ = "UChicago"
    metadata = base.PrimitiveMetadata({
        "algorithm_types": ['HIDDEN_MARKOV_MODEL', 'RANDOM_WALK',
                            'VARIABLE_ORDER_MARKOV_MODEL'],
        "name": "datasmash.d3m_Quantizer",
        "primitive_family": "TIME_SERIES_CLASSIFICATION",
        "python_path": "d3m.primitives.datasmash.d3m_Quantizer",
        "source": {'name': 'UChicago'},
        "version": __version__,
        "id": "3b593a75-fd8f-4779-8489-2ab69e4bf55a",
        'installation': [
            {'type': base.PrimitiveInstallationType.PIP,
             'package': 'datasmash',
             'version': __version__
            }
        ],
        "keywords": [
            'time',
            'series',
            'data smashing',
            'data-smashing',
            'data_smashing',
            'datasmashing',
            'classification',
            'parameter-free',
            'hyperparameter-free'
        ]
    })


    def __init__(self, *,
                 hyperparams: Hyperparams,
                 random_seed: int = 0,
                 docker_containers: Dict[str, DockerContainer] = None,
                 _verbose: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed,
                         docker_containers=docker_containers)

        self._qtz = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """
        outputs argument should be specified as None
        """
        df=inputs
        assert 'class' in df, 'Data frame doesn\'t have the class column'
        collumn_names = list(df.loc[:, df.columns != 'class'])
        assert all(ptypes.is_numeric_dtype(df[col]) for col in df), 'All data in dataframe has to be numeric'
        assert all(isinstance(item, int) for item in collumn_names), 'All but class collumn should have intiger names'
        if os.path.exists('toQuantize'):
            shutil.rmtree('toQuantize')
        os.mkdir('toQuantize')
        os.mkdir('toQuantize/channel_0')
        file = open(os.path.join('toQuantize/channel_0',"library_list"),"w")   
        classes = list(set(df['class']))
        for i in classes:
            outfile = "train_class_" + str(i)
            df_i = df.loc[df.index[df['class'] == i]]
            df_i.loc[:, df.columns != 'class'].to_csv(os.path.join('toQuantize/channel_0', outfile), sep=' ', index=False, header=False)
            file.write(outfile+" "+str(i)+" "+ str(df_i.shape[0]) + " " +"\n")
        file.close() 
        return None


    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        self._qtz = Quantizer(problem_type='supervised', multi_partition=False,
                        featurization=None)
        self._qtz.fit_transform("./toQuantize/channel_0")

        self._fitted = True
        return CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None,
                iterations: int = None) -> CallResult[Outputs]:
        if 'class' in inputs:
            inputs = inputs.loc[:, inputs.columns != 'class']
        collumn_names = list(inputs)
        assert all(isinstance(item, int) for item in collumn_names), 'All but class collumn should be an intiger'
        if os.path.isfile(os.path.join('toQuantize/channel_0', "test")):
            os.remove(os.path.join('toQuantize/channel_0', "test"))
        inputs.to_csv(os.path.join('toQuantize/channel_0', "test"), sep=' ', index=False, header=False)
        to_Return = self._qtz.transform(os.path.join('toQuantize/channel_0', "test"))
        return to_Return

    def get_params(self) -> Params:
        """
        A noop
        """
        return None

    def set_params(self, *, params: Params) -> None:
        """
        A noop
        """
        return None

