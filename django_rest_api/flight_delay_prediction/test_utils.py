from datetime import datetime

import pytest

from flight_delay_prediction.weather.weather_api import WeatherAPI
from flight_delay_prediction.utils import get_minutes_timedelta


@pytest.mark.parametrize(
    "coords_1, coords_2, dt_1, dt_2, result",
    [
        (
            {'lat': 40.683, 'long': -73.944},
            {'lat': 33.943, 'long': -118.408},
            datetime.strptime('06/08/20 07:40', WeatherAPI.datetime_format),
            datetime.strptime('06/08/20 10:43', WeatherAPI.datetime_format),
            363
        ),
        (
            {'lat': 33.943, 'long': -118.408},
            {'lat': 40.683, 'long': -73.944},
            datetime.strptime('06/08/20 15:15', WeatherAPI.datetime_format),
            datetime.strptime('06/08/20 23:57', WeatherAPI.datetime_format),
            342
        )
    ]
)
def test_get_minutes_timedelta(coords_1, coords_2, dt_1, dt_2, result):
    assert get_minutes_timedelta(coords_1, coords_2, dt_1, dt_2) == result


if __name__ == '__main__':
    pytest.main(['-v', __file__])
