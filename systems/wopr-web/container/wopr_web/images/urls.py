from django.urls import path

from . import views

urlpatterns = [
    path("", views.images_index, name="images_index"),
    path(
        "images_show_dir_selector",
        views.show_dir_selector,
        name="images_show_dir_selector",
    ),
    path("images_ondisk", views.images_ondisk, name="images_ondisk"),
    path("images_indb", views.images_indb, name="images_indb"),
    path("add_images_to_db", views.add_images_to_db, name="add_images_to_db"),
    path(
        "move_images_to_archive",
        views.move_images_to_archive,
        name="move_images_to_archive",
    ),
    path(
        "images_ls_list_projects",
        views.images_ls_list_projects,
        name="images_ls_list_projects",
    ),
    path("images_ls_projfile", views.images_ls_projfile, name="images_ls_projfile"),
    path("images_games_index", views.images_games_index, name="images_games_index"),
    path(
        "images_games_details", views.images_games_details, name="images_games_details"
    ),
    path("change_image_game", views.change_image_game, name="change_image_game"),
]
