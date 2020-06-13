import factory
from .models import WeatherForecast
from datetime import datetime


# Create your tests here.
class DjangoWeatherForecastFactory(factory.DjangoModelFactory):
    class Meta:
        model = WeatherForecast

    # iata_code = 'DL'
    temperature = 65
    precipitation = 0
    visibility = 9.5
    wind_speed = 8
    dt = datetime.now()


class MogoWeatherForecastFactory(factory.MogoFactory):
    class Meta:
        model = WeatherForecast

    # iata_code = 'DL'
    temperature = 65
    precipitation = 0
    visibility = 9.5
    wind_speed = 8
    dt = datetime.now()
