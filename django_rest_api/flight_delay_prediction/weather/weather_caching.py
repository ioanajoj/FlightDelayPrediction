from datetime import datetime

from flight_delay_prediction.constant import TEMPERATURES, PRECIPITATION, VISIBILITY, WINDSPEED, DATETIME_FORMAT
from flight_delay_prediction.models import WeatherForecast, WeatherSummary
from flight_delay_prediction.weather.weather_api import WeatherAPI


class WeatherPool:
    @classmethod
    def get_weather(cls, iata_code, dt, location):
        """
        Retrieve weather either from DB or from the API
        :param iata_code: three letter code
        :param dt: string of the format DATETIME_FORMAT
        :param location: AIRPORT['origin'] or AIRPORT['destination']
        :return:
        """
        # check db
        db_weather = cls.request_db(iata_code, dt, location)
        if db_weather:
            return db_weather
        # request from API
        weather = cls.request_weather(iata_code, dt, location)
        return weather

    @classmethod
    def request_db(cls, iata_code, dt, location):
        dt = datetime.strptime(dt, DATETIME_FORMAT).replace(minute=0)
        result = WeatherForecast.objects.filter(iata_code=iata_code, dt=dt).order_by('-id').first()
        if not result:
            result = WeatherSummary.objects.filter(iata_code=iata_code, month=dt.month).first()
        if result:
            return {TEMPERATURES[location]: result.temperature,
                    PRECIPITATION[location]: 0,
                    VISIBILITY[location]: result.visibility,
                    WINDSPEED[location]: result.wind_speed}
        return None

    @classmethod
    def request_weather(cls, iata_code, dt, location):
        return WeatherAPI.get_weather(iata_code, dt, location)
