from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start_training/", views.start_training, name="start_training"),
]
