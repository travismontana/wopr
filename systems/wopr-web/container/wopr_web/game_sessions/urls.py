from django.urls import path

from . import views

urlpatterns = [
    path("", views.gs_index, name="gs_index"),
    path("new/", views.gs_new_form, name="gs_new"),
    path("existing/", views.gs_existing, name="gs_existing"),
    path("<int:session_id>", views.gs_view_specific, name="gs_view_specific"),
    path("game/new/", views.game_new_form, name="game_new_form"),
    path("game/<int:game_id>", views.game_view_specific, name="game_view_specific"),
    path("game/list/", views.game_list, name="game_list"),
    path(
        "player/<int:player_id>",
        views.player_view_specific,
        name="player_view_specific",
    ),
    path("player/new/", views.player_new_form, name="player_new_form"),
    path("players/", views.player_list, name="player_list"),
    path(
        "add_player_to_session/<int:session_id>/",
        views.add_player_to_session,
        name="add_player_to_session",
    ),
    path("take_captures", views.take_captures, name="take_captures"),
]
