from datetime import datetime
import logging

import pandas as pd
from requests import Request

from flight_delay_prediction.constant import TEMPERATURES, PRECIPITATION, WINDSPEED, VISIBILITY
from flight_delay_prediction.models import WeatherSummary, WeatherForecast
from flight_delay_prediction.predict.input_builder import Resources
from flight_delay_prediction.utils import day_difference


class WeatherAPI:
    datetime_format = '%d/%m/%y %H:%M'
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    _api_key = 'IMHAUADKACEIW04W4P08KNMFI'
    _api_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata'
    _history_summary_ep = '/historysummary'
    _forecast_ep = '/forecast'
    logger = logging.getLogger(__name__)

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
    def get_weather(cls, iata_code, forecast_datetime, location) -> dict:
        # use timezone.now()
        coords = Resources.airport_codes[iata_code]
        lat, long = coords['lat'], coords['long']
        current_datetime = datetime.now()
        forecast_datetime = datetime.strptime(forecast_datetime, cls.datetime_format)
        if day_difference(current_datetime, forecast_datetime) >= 15:
            df = cls._get_historical(lat, long)
            cls._save_summary(iata_code, df)
            df = df[df['Period'] == cls.months[forecast_datetime.month - 1]]
            return {TEMPERATURES[location]: df['Temperature'].to_numpy()[0],
                    # PRECIPITATION[location]: df['Precipitation Mean'].to_numpy()[0],
                    PRECIPITATION[location]: 0,
                    VISIBILITY[location]: df['Visibility'].to_numpy()[0],
                    WINDSPEED[location]: df['Wind Speed Mean'].to_numpy()[0]}
        else:
            df = cls._get_forecast(lat, long)
            cls._save_forecast(iata_code, df)
            forecast_datetime = forecast_datetime.replace(minute=0)
            df = df[df['Date time'] == forecast_datetime]
            return {TEMPERATURES[location]: df['Temperature'].to_numpy()[0],
                    PRECIPITATION[location]: df['Precipitation'].to_numpy()[0],
                    VISIBILITY[location]: 9.5,
                    WINDSPEED[location]: df['Wind Speed'].to_numpy()[0]}

    @classmethod
    def _get_historical(cls, lat, long) -> dict:
        """
        Return a historical summary of weather data for the given coordinates
        during the month given in the forecast_datetime
        :param lat: float
        :param long: float
        :return: dataframe having 12 rows for each month and columns for temperature, wind speed,
        precipitation and visibility
        """
        params = {'location': ','.join([str(lat), str(long)]), 'chronoUnit': 'months', 'breakBy': 'self',
                  'unitGroup': 'us', 'dailySummaries': 'true', 'contentType': 'csv',
                  'key': WeatherAPI._api_key}
        request = Request('GET', cls._api_url + cls._history_summary_ep, params=params).prepare()
        df = pd.read_csv(request.url)
        return df

    @classmethod
    def _get_forecast(cls, lat, long) -> dict:
        """
        Return weather forecast data for the given coordinates at the forecast_datetime
        :param lat: float
        :param long: float
        :return: pandas dataframe having rows for hourly forecast for 15 days (~377) and columns for
        temperature, wind speed, precipitation
        """
        params = {'location': ','.join([str(lat), str(long)]), 'aggregateHours': 1, 'unitGroup': 'us',
                  'contentType': 'csv', 'key': cls._api_key}
        request = Request('GET', cls._api_url + cls._forecast_ep, params=params).prepare()
        df = pd.read_csv(request.url)
        df['Date time'] = pd.to_datetime(df['Date time'])
        return df

    @classmethod
    def _save_summary(cls, iata_code, df):
        temperature = df['Temperature']
        precipitation = df['Precipitation']
        visibility = df['Visibility']
        wind_speed = df['Wind Speed Mean']
        for index, month in enumerate(cls.months):
            summary = WeatherSummary(iata_code=iata_code, month=month,
                                     temperature=temperature[index],
                                     precipitation=precipitation[index],
                                     visibility=visibility[index],
                                     wind_speed=wind_speed[index])
            summary.save()
            cls.logger.info(f'Saved summary for {iata_code} in {month}')

    @classmethod
    def _save_forecast(cls, iata_code, df):
        for index in df.shape[0]:
            dt = df['Date time'][index]
            forecast = WeatherForecast(iata_code=iata_code, dt=df['Date time'][index],
                                       temperature=df['Temperature'][index],
                                       precipitation=df['Precipitation'][index],
                                       visibility=9,
                                       wind_speed=df['Wind Speed Mean'][index])
            forecast.save()
            cls.logger.info(f'Saved forecast {iata_code} in {dt}')

