from django.urls import path

from . import views

urlpatterns = [
    path("", views.cameras_index, name="cameras_index"),
    path("grab_snapshot/", views.grab_snapshot, name="grab_snapshot"),
]
