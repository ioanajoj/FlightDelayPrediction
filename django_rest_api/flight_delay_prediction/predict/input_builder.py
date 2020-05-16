import pickle
import glob
import numpy as np
import pandas as pd

from flight_delay_prediction.constant import CATEGORICAL_INPUTS, CONTINUOUS_INPUTS
from flight_delay_prediction.predict.errors import *
import tensorflow.keras.models as models
from flight_delay_prediction.utils import cached_classproperty


class ModelInputBuilder:
    def __init__(self, input_names):
        self.input_names = input_names
        self.inputs = {}

    def set_weather(self, iata_code_1, iata_code_2):
        pass

    def set(self, name, value):
        try:
            self.inputs[name] = value
        except KeyError:
            raise NoPreprocessObjectError(f'Could not find a preprocessing item for {name} input')

    def _is_valid(self):
        return self.inputs.keys() == self.input_names

    def build(self):
        if self._is_valid():
            return self.inputs
        raise IncompleteModelInputError(f'{self.inputs.keys() - self.input_names}'
                                        f'inputs are missing from ModelInputBuilder')


class ResourcesAccess:
    @classmethod
    def preprocess_categorical(cls, key, value):
        return Resources.preprocess_objects[key].transform(np.array(value).reshape(-1, 1))

    @classmethod
    def preprocess_continuous(cls, keys_values):
        data = np.zeros(len(CONTINUOUS_INPUTS))
        for i, keys in enumerate(CONTINUOUS_INPUTS):
            data[i] = keys_values[keys]
        return Resources.preprocess_objects['transformer'].transform(data.reshape(1, -1))

    @classmethod
    def predict(cls, keys_values):
        # prepare categorical inputs
        categorical = []
        for key in CATEGORICAL_INPUTS:
            categorical.append(cls.preprocess_categorical(key, keys_values[key])[0])
        # prepare continuous inputs
        cont = cls.preprocess_continuous(keys_values)
        model_input = categorical + [cont]
        return Resources.model.predict(model_input)


class Resources:
    # resources_path = f'{settings.BASE_DIR}\\resources'
    resources_path = 'C:\\Users\\joj\\PycharmProjects\\django_rest_api\\resources'
    preprocess_path = f'{resources_path}\\preprocessing\\'
    model_path = f'{resources_path}\\keras_model'

    """
    Get a mapping of preprocessing objects
    :return dictionary of keys being the filenames without extension and values the objects
    """
    @cached_classproperty
    def preprocess_objects(cls) -> dict:
        preprocess_objects = {}
        for file_path in glob.glob(cls.preprocess_path + '*.pkl'):
            file_name = file_path.split('\\')[-1].split('.')[0]
            obj = pickle.load(open(file_path, 'rb'))
            preprocess_objects[file_name] = obj
        print('Loaded preprocessing objects')
        return preprocess_objects

    """
    Returns the pre-trained Keras model loaded from model.json and model.h5 files
    """
    @cached_classproperty
    def model(cls):
        # load json and create model
        json_file = open(cls.model_path + '\\model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = models.model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(cls.model_path + "\\model.h5")
        print("Loaded model from disk")
        return loaded_model

    """
    Returns a mapping of the airport code to its geographical coordinates
    :return {'iata_code':{'lat':float, 'long':float}, ...}
    """
    @cached_classproperty
    def airport_codes(cls):
        df = pd.read_csv(cls.resources_path + '\\usa-airports.csv')
        df = df[['iata_code', 'latitude_deg', 'longitude_deg']]
        df = df.rename(columns={'latitude_deg': 'lat', 'longitude_deg': 'long'})
        df = df.round(3)
        df = df.set_index('iata_code')
        return df.to_dict('iata_code')
