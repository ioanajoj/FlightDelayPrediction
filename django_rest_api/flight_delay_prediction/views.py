from django.http import HttpResponse
from django.shortcuts import render
from flight_delay_prediction.predict.input_builder import ModelInputBuilder

# move this somewhere else
input_names = {'carrier_code', 'origin_airport', 'destination_airport', 'day', 'month', 'weekday',
               'scheduled_departure_dt', 'scheduled_elapsed_time',
               'temperature', 'precipitation', 'visibility', 'wind_speed'}


# Create your views here.
def index(request):
    # input = ModelInputBuilder(input_names)
    print(request.GET)
    return HttpResponse("Hello, world. You're at the index.")
