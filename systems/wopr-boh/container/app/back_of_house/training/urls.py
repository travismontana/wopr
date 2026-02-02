from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start_training/", views.start_training, name="start_training"),
    path("training_detail/", views.training_detail, name="training_detail"),
    path("new_training/", views.new_training, name="new_training"),
    path("generate_dataset/", views.generate_dataset, name="generate_dataset"),
]
