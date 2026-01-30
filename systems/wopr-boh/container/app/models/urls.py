from django.urls import path

from . import views

urlpatterns = [
    path("", views.model_index, name="model_index"),
    path("<int:id>", views.model_details, name="model_details"),
    path("model_add", views.model_add, name="model_add"),
    path("model_edit/<int:id>", views.model_edit, name="model_edit"),
    path("model_delete/<int:id>", views.model_delete, name="model_delete"),
    path("model_family_add", views.model_family_add, name="model_family_add"),
    path(
        "model_family_edit/<int:id>", views.model_family_edit, name="model_family_edit"
    ),
    path(
        "model_family_details/<int:id>",
        views.model_family_details,
        name="model_family_details",
    ),
    path(
        "model_family_delete/<int:id>",
        views.model_family_delete,
        name="model_family_delete",
    ),
    path(
        "model_family_bulk_add",
        views.model_family_bulk_add,
        name="model_family_bulk_add",
    ),
]
