from django.urls import path

from . import views

urlpatterns = [
    path("", views.cameras_index, name="cameras_index"),
    path("grab_snapshot/", views.grab_snapshot, name="grab_snapshot"),
    path("c950_stream/", views.c950_stream, name="c950_stream"),
    path("c960_stream/", views.c960_stream, name="c960_stream"),
]
