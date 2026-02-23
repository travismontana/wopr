from django.urls import path

from . import views

urlpatterns = [
    path("", views.cameras_index, name="cameras_index"),
]