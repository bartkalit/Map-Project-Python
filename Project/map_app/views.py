from django.shortcuts import render
from django.conf import settings
from .data_processing import MapData
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


mapdata = MapData()


def dashboard(request):
    return render(request, "base.html")

def travel_time(request):
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'travel-time.html', context)

def hop_friend(request):
    return render(request, 'hop-friend.html')

def travel_plan(request):
    return render(request, 'travel-plan.html')

def travel_time_update(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        userId = int(data['userId'])
        locations = mapdata.get_last_visited_location(userId).to_json(orient="records")
        print(locations)
        context = {
            'locations' : locations
        }
        return JsonResponse(context)
    else:
        pass