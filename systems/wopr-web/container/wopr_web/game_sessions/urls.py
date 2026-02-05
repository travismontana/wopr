from django.urls import path

from . import views

urlpatterns = [
    path("", views.game_sessions_index, name="game_sessions_index"),
]