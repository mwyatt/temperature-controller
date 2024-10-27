from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import render
from TempApp.models import Settings, TempHistory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotAllowed
import json
import time
from calendar import timegm
from tapo import ApiClient
from dotenv import load_dotenv
import os
import asyncio

# Initialise environment variables
# load_dotenv()

def index(request):

    try:
        on_temp = Settings.objects.get(key='on_temp').value
        off_temp = Settings.objects.get(key='off_temp').value
    except:
        on_temp = 10
        off_temp = 10.2

    return render(request, 'index.html', {
        # "request": request,
        "on_temp": on_temp,
        "off_temp": off_temp,
    })

@csrf_exempt
def getTempHistory(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)

    default_last_seconds = 60 * 10

    from_date = data.get('from_date')
    to_date = data.get('to_date')
    latest = data.get('latest')

    epoch_now = int(time.time())
    epoch_time_end = epoch_now

    if latest == True:
        default_last_seconds = 5

    epoch_time_start = epoch_now - default_last_seconds

    if from_date != None and from_date != "":
        utc_time = time.strptime(from_date, "%Y-%m-%dT%H:%M")
        epoch_time_start = timegm(utc_time)

    if to_date != None and to_date != "":
        utc_time = time.strptime(to_date, "%Y-%m-%dT%H:%M")
        epoch_time_end = timegm(utc_time)

    # get temp history
    temp_history = TempHistory.objects.filter(time_created__range=(epoch_time_start, epoch_time_end))

    time_history = []
    temperature_history = []
    heater_status_history = []
    for temp_history_row in temp_history:
        time_history.append(temp_history_row.time_created)
        temperature_history.append(temp_history_row.current_temp)
        heater_status_history.append(temp_history_row.heater_on)

    return JsonResponse({
        "labels": time_history,
        "data": temperature_history,
        "dataHeater": heater_status_history
    })

@csrf_exempt
def setTemp(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body)

    Settings.objects.update_or_create(key='on_temp', defaults={'value': data.get('on_temp')})
    Settings.objects.update_or_create(key='off_temp', defaults={'value': data.get('off_temp')})
    
    return JsonResponse({
        "status": "success"
    })

def getHeaterPlugStatus(request):
    tapo_username = str(os.getenv('TAPO_USERNAME'))
    tapo_password = os.getenv('TAPO_PASSWORD')
    tapo_ip_address = os.getenv('TAPO_HEATER_IP_ADDRESS')

    # create a tapo api client
    tapo_client = ApiClient(tapo_username, tapo_password)

    async def getStatus():
        device = await tapo_client.p100(tapo_ip_address)
        return await device.get_device_info_json()

    return JsonResponse(asyncio.run(getStatus()))