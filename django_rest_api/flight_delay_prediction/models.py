from django.db import models


# Create your models here.
class WeatherBase(models.Model):
    iata_code = models.CharField(max_length=3)
    temperature = models.FloatField()
    precipitation = models.FloatField()
    visibility = models.FloatField()
    wind_speed = models.FloatField()


class WeatherSummary(WeatherBase):
    month = models.IntegerField()


class WeatherForecast(WeatherBase):
    dt = models.DateTimeField()
