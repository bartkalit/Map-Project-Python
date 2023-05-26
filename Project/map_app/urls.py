from django.urls import path
from . import views

urlpatterns = [
    path("", views.travel_time, name='ravel-time'),
    path('travel-time', views.travel_time, name='travel-time'),
    path('hop-friend', views.hop_friend, name='hop-friend'),
    path('travel-plan', views.travel_plan, name='travel-plan'),
    path('travel-time-update', views.travel_time_update, name='travel-time-update'),
]