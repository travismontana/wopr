from django.urls import path

from . import views

urlpatterns = [
    path("", views.images_index, name="images_index"),
    path("images_ondisk", views.images_ondisk, name="images_ondisk"),
    path("images_indb", views.images_indb, name="images_indb"),
]