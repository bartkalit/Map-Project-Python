from django.shortcuts import render
from django.conf import settings
from .data_processing import MapData
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


map_data = MapData()


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
        loc_quantity = 10
        locations = map_data.get_k_closest_locations_for_user(userId, loc_quantity, 'bt')
        print(locations)
        context = {
            'locations' : locations.to_json(orient="records")
        }
        return JsonResponse(context)
    else:
        pass