from datetime import datetime

import pandas as pd
from requests import Request

from flight_delay_prediction.constant import TEMPERATURES, PRECIPITATION, WINDSPEED, VISIBILITY


class WeatherAPI:
    datetime_format = '%d/%m/%y %H:%M'
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    _api_key = 'IMHAUADKACEIW04W4P08KNMFI'
    _api_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata'
    _history_summary_ep = '/historysummary'
    _forecast_ep = '/forecast'

    """
    Return data about weather
    • If forecast_datetime is within 15 days from current datetime, then the weather retrieved
    will be a real forecast
    • If forecast_datetime is anytime later than 15 days from current_datetime, then the weather data
    is a historical summary based on previous years
    :param lat: float
    :param long: float
    :param forecast_datetime: string of format '%d/%m/%y %H:%M'
    :return: dictionary containing values for keys: temperature, visibility, precipitation, wind speed
    """
    @classmethod
    def get_weather(cls, lat, long, forecast_datetime, location) -> dict:
        # use timezone.now()
        current_datetime = datetime.now()
        forecast_datetime = datetime.strptime(forecast_datetime, cls.datetime_format)
        if cls._exceeds_15_days(current_datetime, forecast_datetime):
            return cls._get_historical(lat, long, forecast_datetime, location)
        else:
            return cls._get_forecast(lat, long, forecast_datetime, location)

    """
    Return a historical summary of weather data for the given coordinates 
    during the month given in the forecast_datetime
    :param lat: float
    :param long: float
    :param forecast_datetime: datetime
    :return: dictionary containing values for keys: temperature, visibility, precipitation, wind speed
    """
    @classmethod
    def _get_historical(cls, lat, long, forecast_datetime, location) -> dict:
        params = {'location': ','.join([str(lat), str(long)]), 'chronoUnit': 'months', 'breakBy': 'self',
                  'unitGroup': 'us', 'dailySummaries': 'true', 'contentType': 'csv',
                  'key': WeatherAPI._api_key}
        request = Request('GET', cls._api_url + cls._history_summary_ep, params=params).prepare()
        df = pd.read_csv(request.url)
        df = df[df['Period'] == cls.months[forecast_datetime.month - 1]]
        df = df[['Temperature', 'Wind Speed Mean',
                 'Precipitation Mean', 'Visibility',
                 'Minimum Temperature Mean', 'Maximum Temperature Mean']]
        return {TEMPERATURES[location]: df['Temperature'].to_numpy()[0],
                PRECIPITATION[location]: df['Precipitation Mean'].to_numpy()[0],
                VISIBILITY[location]: df['Visibility'].to_numpy()[0],
                WINDSPEED[location]: df['Wind Speed Mean'].to_numpy()[0]}

    """
    Return weather forecast data for the given coordinates at the forecast_datetime
    :param lat: float
    :param long: float
    :param forecast_datetime: datetime
    :return: dictionary containing values for keys: temperature, visibility, precipitation, wind speed
    """
    @classmethod
    def _get_forecast(cls, lat, long, forecast_datetime, location) -> dict:
        params = {'location': ','.join([str(lat), str(long)]), 'aggregateHours': 1, 'unitGroup': 'us',
                  'contentType': 'csv', 'key': cls._api_key}
        request = Request('GET', cls._api_url + cls._forecast_ep, params=params).prepare()
        df = pd.read_csv(request.url)
        forecast_datetime = forecast_datetime.replace(minute=0)
        df['Date time'] = pd.to_datetime(df['Date time'])
        df = df[df['Date time'] == forecast_datetime]
        # Visibility is apparently not available :(
        df = df[['Temperature', 'Precipitation', 'Wind Speed']]
        return {TEMPERATURES[location]: df['Temperature'].to_numpy()[0],
                PRECIPITATION[location]: df['Precipitation'].to_numpy()[0],
                VISIBILITY[location]: 9.5,
                WINDSPEED[location]: df['Wind Speed'].to_numpy()[0]}

    """
    Checks if the difference between the two daytime objects is greater than 15 days
    :param daytime1: datetime
    :param daytime2: datetime
    :return: boolean
    """
    @staticmethod
    def _exceeds_15_days(daytime1, daytime2) -> bool:
        if daytime1 > daytime2:
            daytime1, daytime2 = daytime2, daytime1
        return (daytime2 - daytime1).days >= 15
