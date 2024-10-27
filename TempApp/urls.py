from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("temp-history", views.getTempHistory, name="getTempHistory"),
    path("set-temp", views.setTemp, name="setTemp"),
    path("heater-plug-status", views.getHeaterPlugStatus, name="getHeaterPlugStatus"),
]