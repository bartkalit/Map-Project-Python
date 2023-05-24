from django.urls import path
from .views import dashboard

app_name = "mapApp"

urlpatterns = [
    path("", dashboard, name="index"),
]