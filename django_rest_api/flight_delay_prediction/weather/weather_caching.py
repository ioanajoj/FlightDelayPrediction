from datetime import datetime

from flight_delay_prediction.constant import TEMPERATURES, PRECIPITATION, VISIBILITY, WINDSPEED, DATETIME_FORMAT
from flight_delay_prediction.models import WeatherForecast, WeatherSummary
from flight_delay_prediction.resources_loader import Resources
from flight_delay_prediction.weather.weather_api import WeatherAPI


class WeatherPool:
    @classmethod
    def get_weather(cls, iata_code, dt, location):
        """

        :param iata_code: three letter code
        :param dt: string of the format DATETIME_FORMAT
        :param location: AIRPORT['origin'] or AIRPORT['destination']
        :return:
        """
        # check in db
        db_weather = cls.retrieve_db(iata_code, dt, location)
        if db_weather:
            return db_weather
        # request from API
        weather = cls.request_weather(iata_code, dt, location)
        return weather

    @classmethod
    def retrieve_db(cls, iata_code, dt, location):
        dt = datetime.strptime(dt, DATETIME_FORMAT)
        result = WeatherForecast.objects.filter(iata_code=iata_code, dt=dt)
        if not result:
            result = WeatherSummary.objects.filter(iata_code=iata_code, month=dt.month)
        if result:
            weather = result[0]
            return {TEMPERATURES[location]: weather.temperature,
                    PRECIPITATION[location]: weather.precipitation,
                    VISIBILITY[location]: weather.visibility,
                    WINDSPEED[location]: weather.wind_speed}
        return None

    @classmethod
    def request_weather(cls, iata_code, dt, location):
        return WeatherAPI.get_weather(iata_code, dt, location)
