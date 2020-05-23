from datetime import datetime

from flight_delay_prediction.constant import CATEGORICAL_INPUTS, CONTINUOUS_INPUTS, AIRPORTS, INPUT_NAMES, TEMPERATURES, \
    PRECIPITATION, VISIBILITY, WINDSPEED
from flight_delay_prediction.errors import *
from flight_delay_prediction.resources_loader import Resources
from flight_delay_prediction.weather.weather_api import WeatherAPI
from flight_delay_prediction.utils import get_minutes_timedelta
from flight_delay_prediction.weather.weather_caching import WeatherPool


class ModelInputBuilder:
    """
    Params need to contain values for keys:
    carrier_code, origin_airport, destination_airport, origin_dt, destination_dt
    """

    def __init__(self, params, mock_weather=False):
        if not params.keys() == {'carrier_code',
                                 'origin_airport', 'destination_airport',
                                 'origin_dt', 'destination_dt'}:
            raise WrongRequestParameters()
        self.inputs = {}
        self.params = params
        self.mock_weather = mock_weather
        self.set_categorical()
        self.set_continuous()

    def get_weather(self):
        weather = {}
        weather_origin = self._access_weather(self.params['origin_airport'],
                                              self.params['origin_dt'],
                                              AIRPORTS['origin'])
        weather.update(weather_origin)
        weather_destination = self._access_weather(self.params['destination_airport'],
                                                   self.params['destination_dt'],
                                                   AIRPORTS['destination'])
        weather.update(weather_destination)
        return weather

    def _access_weather(self, iata_code, dt, location):
        if self.mock_weather:
            return {TEMPERATURES[location]: 67, PRECIPITATION[location]: 0,
                    VISIBILITY[location]: 9, WINDSPEED[location]: 16}
        weather = WeatherPool.get_weather(iata_code, dt, location)
        return weather

    def set_categorical(self):
        categorical = {'carrier_code': self.params['carrier_code'],
                       'origin_airport': self.params['origin_airport'],
                       'destination_airport': self.params['destination_airport'],
                       'day': str(datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).day),
                       'month': str(datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).month),
                       'weekday': str(
                           datetime.strptime(self.params['origin_dt'], WeatherAPI.datetime_format).weekday())}
        self.inputs.update(categorical)
        assert categorical.keys() == set(CATEGORICAL_INPUTS)

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
        assert continuous.keys() == set(CONTINUOUS_INPUTS)

    def _is_valid(self):
        return self.inputs.keys() == INPUT_NAMES

    def build(self):
        if self._is_valid():
            return self.inputs
        raise IncompleteModelInputError(f'{self.inputs.keys() - INPUT_NAMES}'
                                        f'inputs are missing from ModelInputBuilder')
