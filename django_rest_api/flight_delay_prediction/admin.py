from django.contrib import admin
from flight_delay_prediction.models import WeatherSummary, WeatherForecast


# Register your models here.
@admin.register(WeatherForecast, WeatherSummary)
class WeatherAdmin(admin.ModelAdmin):
    pass
