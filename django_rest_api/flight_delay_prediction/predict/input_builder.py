import pickle
import glob
from datetime import datetime

import numpy as np
import pandas as pd
import tensorflow.keras.models as models

from flight_delay_prediction.constant import CATEGORICAL_INPUTS, CONTINUOUS_INPUTS, AIRPORTS, INPUT_NAMES
from flight_delay_prediction.predict.errors import *
from flight_delay_prediction.predict.weather_api import WeatherAPI
from flight_delay_prediction.utils import cached_classproperty
from flight_delay_prediction.utils import get_minutes_timedelta


class ModelInputBuilder:
    """
    Params need to contain values for keys:
    carrier_code, origin_airport, destination_airport, origin_dt, destination_dt
    """

    def __init__(self, params):
        assert params.keys() == {'carrier_code',
                                 'origin_airport', 'destination_airport',
                                 'origin_dt', 'destination_dt'}
        self.inputs = {}
        self.params = params
        self.set_categorical()
        self.set_continuous()

    def get_weather(self):
        weather = {}
        weather_origin = ModelInputBuilder._access_weather(self.params['origin_airport'],
                                                           self.params['origin_dt'],
                                                           AIRPORTS['origin'])
        weather.update(weather_origin)
        weather_destination = ModelInputBuilder._access_weather(self.params['destination_airport'],
                                                                self.params['destination_dt'],
                                                                AIRPORTS['destination'])
        weather.update(weather_destination)
        return weather

    @staticmethod
    def _access_weather(iata_code, dt, location):
        coords = Resources.airport_codes[iata_code]
        weather = WeatherAPI.get_weather(coords['lat'], coords['long'], dt, location)
        return weather

    def set_categorical(self):
        categorical = {'carrier_code': self.params['carrier_code'],
                       'origin_airport': self.params['origin_airport'],
                       'destination_airport': self.params['destination_airport'],
                       'day': datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).day,
                       'month': datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).month,
                       'weekday': datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).weekday()}
        self.inputs.update(categorical)
        assert categorical.keys() == CATEGORICAL_INPUTS

    def set_continuous(self):
        continuous = self.get_weather()
        # set number of seconds from midnight
        departure = datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format)
        departure = (departure - datetime(departure.year, departure.month, departure.day)).seconds // 60
        continuous['scheduled_departure_dt'] = departure
        # set in air time of flight
        continuous['scheduled_elapsed_time'] = get_minutes_timedelta(
            Resources.airport_codes[self.inputs['origin_airport']],
            Resources.airport_codes[self.inputs['destination_airport']],
            datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format),
            datetime.strptime(self.params['destination_dt'], WeatherAPI.datetime_format)
        )
        self.inputs.update(continuous)
        assert continuous.keys() == CONTINUOUS_INPUTS

    def _is_valid(self):
        return self.inputs.keys() == INPUT_NAMES

    def build(self):
        if self._is_valid():
            return self.inputs
        raise IncompleteModelInputError(f'{self.inputs.keys() - INPUT_NAMES}'
                                        f'inputs are missing from ModelInputBuilder')


class ResourcesAccess:
    @classmethod
    def preprocess_categorical(cls, key, value):
        try:
            return Resources.preprocess_objects[key].transform(np.array(value).reshape(-1, 1))
        except ValueError:
            raise UnknownCategoryError(f'Error for key {key}', f'Could not find value {value}')

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
