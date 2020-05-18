AIRPORTS = {'origin': 'x', 'destination': 'y'}
TEMPERATURES = {'x': 'temperature_x', 'y': 'temperature_y'}
PRECIPITATION = {'x': 'precipitation_x', 'y': 'precipitation_y'}
VISIBILITY = {'x': 'visibility_x', 'y': 'visibility_y'}
WINDSPEED = {'x': 'wind_speed_x', 'y': 'wind_speed_y'}
CATEGORICAL_INPUTS = ['carrier_code', 'day', 'weekday', 'month', 'origin_airport', 'destination_airport']
CONTINUOUS_INPUTS = ['scheduled_elapsed_time', 'scheduled_departure_dt',
                     'temperature_x', 'precipitation_x', 'visibility_x', 'wind_speed_x',
                     'temperature_y', 'precipitation_y', 'visibility_y', 'wind_speed_y']
INPUT_NAMES = {'carrier_code', 'origin_airport', 'destination_airport', 'day', 'month', 'weekday',
               'scheduled_departure_dt', 'scheduled_elapsed_time',
               'temperature', 'precipitation', 'visibility', 'wind_speed'}
