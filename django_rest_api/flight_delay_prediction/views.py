from django.http import HttpResponse
from django.shortcuts import render

from flight_delay_prediction.constant import INPUT_NAMES
from flight_delay_prediction.predict.input_builder import ModelInputBuilder, ResourcesAccess


# Create your views here.
def index(request):
    params = request.GET
    print(params)
    inputs = ModelInputBuilder(params)
    prediction = None
    try:
        prediction = ResourcesAccess.predict(inputs.inputs)
        print(prediction)
    except Exception as ex:
        print(ex)
    return HttpResponse(f"Hello, world. You're at the index. {prediction}")
