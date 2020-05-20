from datetime import datetime
import pytest

from flight_delay_prediction.models import WeatherForecast
from flight_delay_prediction.utils import day_difference
from flight_delay_prediction.weather.weather_api import WeatherAPI


@pytest.mark.parametrize(
    "dt1,dt2",
    [
        (
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format),
                datetime.strptime('17/05/20 13:13', WeatherAPI.datetime_format)
        ),
        (
                datetime.strptime('17/05/20 13:13', WeatherAPI.datetime_format),
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format)
        ),
        (
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format),
                datetime.strptime('30/05/20 11:56', WeatherAPI.datetime_format)
        )
    ]
)
def test_not_exceeds_15_days(dt1, dt2):
    assert day_difference(dt1, dt2) < 15


@pytest.mark.parametrize(
    "dt1,dt2",
    [
        (
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format),
                datetime.strptime('17/06/20 13:13', WeatherAPI.datetime_format)
        ),
        (
                datetime.strptime('17/06/20 13:13', WeatherAPI.datetime_format),
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format)
        ),
        (
                datetime.strptime('15/05/20 11:57', WeatherAPI.datetime_format),
                datetime.strptime('30/05/20 11:57', WeatherAPI.datetime_format)
        )
    ]
)
def test_exceeds_15_days(dt1, dt2):
    assert day_difference(dt1, dt2) >= 15


# @pytest.mark.parametrize(
#     "lat,long,dt,location",
#     [
#         (
#             40.683126,
#             -73.944897,
#             datetime.strptime('17/05/20 11:57', WeatherAPI.datetime_format),
#             'x'
#         ),
#         (
#             40.683126,
#             -73.944897,
#             datetime.strptime('17/05/20 11:57', WeatherAPI.datetime_format),
#             'y'
#         )
#     ]
# )
# def test_get_forecast(lat, long, dt, location):
#     weather = WeatherAPI._get_forecast(lat, long, dt, location)
#     assert weather.keys() == {'temperature_'+location, 'precipitation_'+location,
#                               'visibility_'+location, 'wind_speed_'+location}
#
#
# @pytest.mark.parametrize(
#     "lat,long,dt,location",
#     [
#         (
#             40.683126,
#             -73.944897,
#             datetime.strptime('17/06/20 11:57', WeatherAPI.datetime_format),
#             'x'
#         )
#     ]
# )
# def test_get_historical(lat, long, dt, location):
#     weather = WeatherAPI._get_historical(lat, long, dt, location)
#     assert weather.keys() == {'temperature_' + location, 'precipitation_' + location,
#                               'visibility_' + location, 'wind_speed_' + location}
#
#
# @pytest.mark.parametrize(
#     "lat,long,dt,location",
#     [
#         (
#             40.683126,
#             -73.944897,
#             '17/06/20 11:57',
#             'x'
#         ),
#         (
#             40.683126,
#             -73.944897,
#             '17/05/20 11:57',
#             'y'
#         )
#     ]
# )
# def test_get_weather(lat, long, dt, location):
#     weather = WeatherAPI.get_weather(lat, long, dt, location)
#     assert weather.keys() == {'temperature_' + location, 'precipitation_' + location,
#                               'visibility_' + location, 'wind_speed_' + location}

@pytest.mark.django_db
@pytest.mark.parametrize(
    "iata_code,dt,location",
    [
        (
                'JFK',
                '20/5/20 11:57',
                'x'
        ),
        (
                'DCA',
                '20/6/20 11:57',
                'y'
        )
    ]
)
def test_get_forecast(iata_code, dt, location):
    weather = WeatherAPI.get_weather(iata_code, dt, location)
    assert weather.keys() == {'temperature_' + location, 'precipitation_' + location,
                              'visibility_' + location, 'wind_speed_' + location}
    dt = datetime.strptime(dt, WeatherAPI.datetime_format)
    query = WeatherForecast.objects.filter(iata_code=iata_code, dt=dt.replace(minute=0))


if __name__ == '__main__':
    pytest.main(['-v', __file__])
