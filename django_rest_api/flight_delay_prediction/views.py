from django.http import HttpResponse
from django.shortcuts import render

from flight_delay_prediction.constant import INPUT_NAMES
from flight_delay_prediction.predict.input_builder import ModelInputBuilder


# Create your views here.
from flight_delay_prediction.resources_loader import ResourcesAccess


def index(request):
    """
    example: payload = {'carrier_code':'DL','origin_airport':'JFK','destination_airport':'LAX',
                        'origin_dt':'18/12/20 11:00','destination_dt':'18/12/20 14:10'}
            requests.get('http://127.0.0.1:8000/predict', params=payload)
    :param request:
    :return:
    """
    params = request.GET
    print(params)
    inputs = ModelInputBuilder(params, mock_weather=False)
    prediction = None
    try:
        prediction = ResourcesAccess.predict(inputs.inputs)
        print(prediction)
    except Exception as ex:
        print(ex)
        return HttpResponse("Unfortunately something went wrong :)")
    return HttpResponse(f"{round(1 - prediction[0,0], 2)}")

# def predict(carrier_code, origin_airport, destination_airport, origin_dt, destination_dt):
#     payload = {'carrier_code': carrier_code,
#                'origin_airport': origin_airport, 'destination_airport': destination_airport,
#                'origin_dt': origin_dt, 'destination_dt': destination_dt}
#     import requests
#     return requests.get('http://127.0.0.1:8000/predict', params=payload).content
