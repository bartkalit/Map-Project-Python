from django.shortcuts import render
from django.conf import settings
from .src.data_processing import MapData
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
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'hop-friend.html', context)

def travel_plan(request):
    return render(request, 'travel-plan.html')

def travel_time_update(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        userId = int(data['userId'])
        loc_quantity = 10
        locations = map_data.get_k_closest_locations(userId, loc_quantity)
        context = {
            'locations' : locations.to_json(orient="records")
        }
        return JsonResponse(context)
    else:
        pass

def hop_time_update(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        userId = int(data['userId'])
        loc_quantity = 10
        locations = map_data.get_k_closest_2hop_locations(userId, loc_quantity)
        friends = map_data.user_list.get_2_hop_friends_ids(userId)
        chosen_f = locations['user_id'].tolist()
        context = {
            'locations' : locations.to_json(orient="records"),
            'friends' : friends,
            'chosen_f': chosen_f
        }
        return JsonResponse(context)
    else:
        pass