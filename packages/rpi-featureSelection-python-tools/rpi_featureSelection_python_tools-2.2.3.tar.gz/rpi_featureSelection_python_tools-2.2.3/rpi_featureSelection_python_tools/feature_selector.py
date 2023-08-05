# with input in the DataFrame format
# handle categorical values
# update metadata of the dataset

import rpi_feature_selection_toolbox
import os, sys
import typing
import scipy.io
import numpy as np
from sklearn import preprocessing

from d3m import container
from d3m.metadata import base as metadata_base
from d3m.metadata import hyperparams
from d3m.metadata import params
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult
# from . import __version__


Inputs = container.DataFrame
Outputs = container.DataFrame

__all__ = ('IPCMBplus_Selector',)

class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass
    '''
    n_bins = hyperparams.UniformInt(
                            lower=5,
                            upper=15,
                            default=10,
                            description='The maximum number of bins used for continuous variables discretization.'
                            )
    '''


class IPCMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '69845479-0b61-3578-b382-972cd0e61d69',
        'version': '2.1.3',
        'name': 'IPCMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
                'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.IPCMBplus_Selector',
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.MINIMUM_REDUNDANCY_FEATURE_SELECTION
        ],
        'primitive_family': metadata_base.PrimitiveFamily.FEATURE_SELECTION,
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
            
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})      

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.IPCMBplus()), [-1, ])
        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class JMIplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '58a8fe68-74eb-3e21-a823-bfa708010759',
        'version': '2.1.3',
        'name': 'JMIplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.JMIplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.JMIplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class STMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '9d1a2e58-5f97-386c-babd-5a9b4e9b6d6c',
        'version': '2.1.3',
        'name': 'STMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.STMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')
        
        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})       

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.STMBplus()), [-1, ])
        
        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class aSTMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '744687e8-2224-3ef5-92e5-ce66d2ad05d7',
        'version': '2.1.3',
        'name': 'aSTMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.aSTMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.aSTMBplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class sSTMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '976060b2-fb0a-329a-8851-d22b25ebe99a',
        'version': '2.1.3',
        'name': 'sSTMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.sSTMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.sSTMBplus()), [-1, ])
        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass


class F_STMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '37079f49-54d5-3d47-a221-5664c546ff90',
        'version': '2.1.3',
        'name': 'F_STMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_STMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_STMB()), [-1, ])
 
        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass




class F_aSTMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': 'e6217c3c-b2d2-3e6b-82e9-060ffd0b9faf',
        'version': '2.1.3',
        'name': 'F_aSTMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_aSTMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_aSTMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class F_sSTMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_base.PrimitiveMetadata({
        'id': '6285b9fb-26e9-3979-a422-c126ff9448d1',
        'version': '2.1.3',
        'name': 'F_sSTMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.1.3'
            },
            {
                'type': metadata_base.PrimitiveInstallationType.PIP,
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.2.3'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_sSTMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
       # convert categorical values to numerical values for training labels
        LE = preprocessing.LabelEncoder()
        LE = LE.fit(outputs.iloc[:,0])
        self._training_outputs = LE.transform(outputs.iloc[:,0])
        
        # convert cateforical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                LE = preprocessing.LabelEncoder()
                LE = LE.fit(inputs.iloc[:,column_index])
                self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])  
            else:
                temp = list(inputs.iloc[:, column_index].as_matrix())
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = 'nan'
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_sSTMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:
            output = inputs.iloc[:, self._index]
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass

