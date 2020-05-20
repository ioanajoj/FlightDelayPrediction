from datetime import datetime

import pandas as pd
from requests import Request

from flight_delay_prediction.constant import TEMPERATURES, PRECIPITATION, WINDSPEED, VISIBILITY
from flight_delay_prediction.errors import RequestsExceeded
from flight_delay_prediction.models import WeatherSummary, WeatherForecast
from flight_delay_prediction.resources_loader import Resources
from flight_delay_prediction.utils import day_difference


class WeatherResponse:
    def __init__(self, location, temperature=59, precipitation=0, visibility=9, wind_speed=1):
        self.location = location
        self.response = {TEMPERATURES[location]: temperature, PRECIPITATION[location]: precipitation,
                         VISIBILITY[location]: visibility, WINDSPEED[location]: wind_speed}


class WeatherAPI:
    datetime_format = '%d/%m/%y %H:%M'
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    _api_key = 'IMHAUADKACEIW04W4P08KNMFI'
    _api_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata'
    _history_summary_ep = '/historysummary'
    _forecast_ep = '/forecast'

    @classmethod
    def get_weather(cls, iata_code, forecast_datetime, location) -> dict:
        """
        Return data about weather
        • If forecast_datetime is within 15 days from current datetime, then the weather retrieved
        will be a real forecast
        • If forecast_datetime is anytime later than 15 days from current_datetime, then the weather data
        is a historical summary based on previous years
        :param iata_code: three letter string
        :param forecast_datetime: string of format '%d/%m/%y %H:%M'
        :param location: AIRPORT['origin'] or AIRPORT['destination']
        :return: dictionary containing values for keys: temperature, visibility, precipitation, wind speed
        """
        lat, long = Resources.airport_codes[iata_code].values()
        current_datetime = datetime.now()
        forecast_datetime = datetime.strptime(forecast_datetime, cls.datetime_format)
        if day_difference(current_datetime, forecast_datetime) >= 15:
            df = cls._get_historical(lat, long)
            cls._save_summary(iata_code, df)
            df = df[df['Period'] == cls.months[forecast_datetime.month - 1]]
            return WeatherResponse(
                location,
                temperature=df['Temperature'].to_numpy()[0],
                visibility=df['Visibility'].to_numpy()[0],
                wind_speed=df['Wind Speed'].to_numpy()[0]
            ).response
        else:
            df = cls._get_forecast(lat, long)
            cls._save_forecast(iata_code, df)
            forecast_datetime = forecast_datetime.replace(minute=0)
            df = df[df['Date time'] == forecast_datetime]
            return WeatherResponse(
                location,
                temperature=df['Temperature'].to_numpy()[0],
                precipitation=df['Precipitation'].to_numpy()[0],
                wind_speed=df['Wind Speed'].to_numpy()[0]
            ).response

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
        if df.shape[0] == 0:
            raise RequestsExceeded()
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
        if df.shape[0] == 0:
            raise RequestsExceeded()
        df['Date time'] = pd.to_datetime(df['Date time'])
        return df

    @classmethod
    def _save_summary(cls, iata_code, df):
        df = df[['Temperature', 'Precipitation', 'Visibility', 'Wind Speed Mean']]
        df = df.dropna()
        df = df.reset_index()
        temperature = df['Temperature']
        precipitation = df['Precipitation']
        visibility = df['Visibility']
        wind_speed = df['Wind Speed Mean']
        for index, month in enumerate(cls.months):
            WeatherSummary.objects.create(
                iata_code=iata_code, month=index,
                temperature=temperature[index],
                precipitation=precipitation[index],
                visibility=visibility[index],
                wind_speed=wind_speed[index]
            )
            print(f'log: Saved summary for {iata_code} in {month}')

    @classmethod
    def _save_forecast(cls, iata_code, df):
        df = df[['Date time', 'Temperature', 'Precipitation', 'Wind Speed']]
        df = df.dropna()
        df = df.reset_index()
        temperature = df['Temperature']
        precipitation = df['Precipitation']
        wind_speed = df['Wind Speed']
        for index in range(df.shape[0]):
            dt = df['Date time'][index]
            WeatherForecast.objects.create(
                iata_code=iata_code, dt=df['Date time'][index],
                temperature=temperature[index],
                precipitation=precipitation[index],
                visibility=9,
                wind_speed=wind_speed[index]
            )
            print(f'log: Saved forecast for {iata_code} in {dt}')
