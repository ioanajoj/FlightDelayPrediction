import pytest
import numpy as np

from flight_delay_prediction.predict.input_builder import Resources, ResourcesAccess


@pytest.mark.parametrize(
    "key,value",
    [
        ('carrier_code', 'AA'),
        ('day', 31),
        ('origin_airport', 'JFK'),
        ('destination_airport', 'LAX'),
        ('month', '10'),
        ('weekday', '3')
    ]
)
def test_categorical_inputs(key, value):
    assert ResourcesAccess.preprocess_categorical(key, value) == \
           Resources.preprocess_objects[key].transform(np.array(value).reshape(-1, 1))


@pytest.mark.parametrize(
    "keys_values",
    [
        ({'scheduled_elapsed_time': 60, 'scheduled_departure_dt': 480,
          'temperature_x': 16, 'temperature_y': 18,
          'precipitation_x': 0, 'precipitation_y': 0.17,
          'visibility_x': 10, 'visibility_y': 4.5,
          'wind_speed_x': 15, 'wind_speed_y': 6})
    ]
)
def test_continuous_inputs(keys_values):
    assert ResourcesAccess.preprocess_continuous(keys_values).shape == (1, 10)


def test_load_model():
    categ = [4.0, 7.0, 2.0, 0.0, 92.0, 21.0]
    categ = [np.array([x]) for x in categ]
    cont = np.array(
        [-0.38669133, -0.35944303, 0.5141577, -0.35986405, 0.8160906, -0.84814475, -0.35944303, 1.40762412, -0.35986405,
         0.00850574])
    cont = np.array([cont])
    example = categ + [cont]
    assert 0 < Resources.model.predict(example) < 1


@pytest.mark.parametrize(
    "keys_values",
    [
        ({'scheduled_elapsed_time': 60, 'scheduled_departure_dt': 480,
          'temperature_x': 16, 'temperature_y': 18,
          'precipitation_x': 0, 'precipitation_y': 0.17,
          'visibility_x': 10, 'visibility_y': 4.5,
          'wind_speed_x': 15, 'wind_speed_y': 6,
          'carrier_code': 'AA', 'day': 31,
          'origin_airport': 'JFK', 'destination_airport': 'LAX',
          'month': '10', 'weekday': '3'})
    ]
)
def test_model(keys_values):
    assert 0 < ResourcesAccess.predict(keys_values) < 1


@pytest.mark.parametrize(
    "code, lat, log",
    [
        ('JFK', 40.640, -73.779),
        ('LAX', 33.943, -118.408)
    ]
)
def test_airport_codes(code, lat, log):
    coords = Resources.airport_codes[code]
    assert coords['lat'] == lat and coords['long'] == log


if __name__ == '__main__':
    pytest.main(['-v', __file__])
