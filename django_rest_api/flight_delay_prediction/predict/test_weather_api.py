from datetime import datetime
import pytest

from flight_delay_prediction.predict.weather_api import WeatherAPI


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
    assert WeatherAPI._exceeds_15_days(dt1, dt2) is False


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
    assert WeatherAPI._exceeds_15_days(dt1, dt2) is True


@pytest.mark.parametrize(
    "lat,long,dt,location",
    [
        (
            40.683126,
            -73.944897,
            datetime.strptime('17/05/20 11:57', WeatherAPI.datetime_format),
            'x'
        ),
        (
            40.683126,
            -73.944897,
            datetime.strptime('17/05/20 11:57', WeatherAPI.datetime_format),
            'y'
        )
    ]
)
def test_get_forecast(lat, long, dt, location):
    weather = WeatherAPI._get_forecast(lat, long, dt, location)
    assert weather.keys() == {'temperature_'+location, 'precipitation_'+location,
                              'visibility_'+location, 'wind_speed_'+location}


@pytest.mark.parametrize(
    "lat,long,dt,location",
    [
        (
            40.683126,
            -73.944897,
            datetime.strptime('17/06/20 11:57', WeatherAPI.datetime_format),
            'x'
        )
    ]
)
def test_get_historical(lat, long, dt, location):
    weather = WeatherAPI._get_historical(lat, long, dt, location)
    assert weather.keys() == {'temperature_' + location, 'precipitation_' + location,
                              'visibility_' + location, 'wind_speed_' + location}


@pytest.mark.parametrize(
    "lat,long,dt,location",
    [
        (
            40.683126,
            -73.944897,
            '17/06/20 11:57',
            'x'
        ),
        (
            40.683126,
            -73.944897,
            '17/05/20 11:57',
            'y'
        )
    ]
)
def test_get_weather(lat, long, dt, location):
    weather = WeatherAPI.get_weather(lat, long, dt, location)
    assert weather.keys() == {'temperature_' + location, 'precipitation_' + location,
                              'visibility_' + location, 'wind_speed_' + location}


if __name__ == '__main__':
    pytest.main(['-v', __file__])
