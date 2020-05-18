from django.http import HttpResponse
from django.shortcuts import render

from flight_delay_prediction.constant import INPUT_NAMES
from flight_delay_prediction.predict.input_builder import ModelInputBuilder, ResourcesAccess


# Create your views here.
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
    return HttpResponse(f"Hello, world. You're at the index. {prediction[0]}")
