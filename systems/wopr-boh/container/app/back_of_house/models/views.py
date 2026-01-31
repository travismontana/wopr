import threading

from django.shortcuts import render, get_object_or_404, redirect

from core.models import ModelFamily, ModelInfo, ModelVersion, ModelBackup
from django.forms.models import model_to_dict

from .forms import (
    TrainingModelForm,
    TrainingModelFamilyForm,
    TrainingModelVersionForm,
    TrainingModelBackupForm,
    ModelFamilyBulkForm,
)

from .lib.helpers import handle_mf_bulk

from .lib.lib_model import build_vers

# Create your views here.
def model_index(request):
    models = ModelInfo.objects.all()
    model_form = TrainingModelForm()
    model_families = ModelFamily.objects.all()
    model_family_form = TrainingModelFamilyForm()
    context = {
        "models": models,
        "model_families": model_families,
        "model_form": model_form,
        "model_family_form": model_family_form,
    }
    return render(request, "models.html", context)


def model_details(request, id):
    model = get_object_or_404(ModelInfo, pk=id)
    model_cur_version = (
        ModelVersion.objects.filter(model=model).order_by("-created_at").first()
    )
    model_backups = ModelBackup.objects.filter(model_version=model_cur_version)
    context = {
        "model": model,
        "model_dict": model_to_dict(model) if model else {},
        "model_version": model_cur_version,
        "model_version_dict": (
            model_to_dict(model_cur_version) if model_cur_version else {}
        ),
        "model_backups": model_backups,
        "model_backups_dict": (
            [model_to_dict(backup) for backup in model_backups] if model_backups else []
        ),
    }
    return render(request, "model_details.html", context)


def model_add(request):
    if request.method == "POST":
        form = TrainingModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("model_index")
            # Redirect after successful save - where to?
            # return redirect('training_models_homeview')  # needs URL name
    else:
        form = TrainingModelForm()
    return render(request, "model_add.html", {"form": form})


def model_edit(request, id):
    model = get_object_or_404(ModelInfo, pk=id)

    if request.method == "POST":
        form = TrainingModelForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            return redirect("model_index")
            # Redirect after successful save - where to?
            # return redirect('training_models_homeview')  # needs URL name
    else:
        form = TrainingModelForm(instance=model)
    return render(request, "model_edit.html", {"form": form, "model": model})


def model_delete(request, id):
    model = get_object_or_404(ModelInfo, pk=id)
    model.delete()
    return redirect("model_index")


def model_family_details(request, id):
    model_family = get_object_or_404(ModelFamily, pk=id)
    context = {"model_family": model_family}
    return render(request, "model_family_details.html", context)


def model_family_add(request):
    if request.method == "POST":
        form = TrainingModelFamilyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("model_index")
            # Redirect after successful save - where to?
            # return redirect('training_models_homeview')  # needs URL name
    else:
        form = TrainingModelFamilyForm()
    bulk_add_form = ModelFamilyBulkForm()
    return render(
        request, "model_family_add.html", {"form": form, "bulk_add_form": bulk_add_form}
    )


def model_family_edit(request, id):
    model_family = get_object_or_404(ModelFamily, pk=id)
    context = {"model_family": model_family}
    if request.method == "POST":
        form = TrainingModelFamilyForm(request.POST, instance=model_family)
        if form.is_valid():
            form.save()
            return redirect("model_index")
            # Redirect after successful save - where to?
            # return redirect('training_models_homeview')  # needs URL name
    else:
        form = TrainingModelFamilyForm(instance=model_family)
    return render(
        request, "model_family_edit.html", {"form": form, "model_family": model_family}
    )


def model_family_delete(request, id):
    model_family = get_object_or_404(ModelFamily, pk=id)
    model_family.delete()
    return redirect("model_index")


def model_family_bulk_add(request):
    if request.method == "POST":
        form = ModelFamilyBulkForm(request.POST, request.FILES)
        if form.is_valid():
            handle_mf_bulk(request.FILES["file"])
            # Handle file processing here
            return redirect("model_index")
    else:
        form = ModelFamilyBulkForm()
    return render(request, "model_family_bulk_add.html", {"form": form})


def model_version_initial(request, model_id):
    model = get_object_or_404(ModelInfo, pk=model_id)
    if request.method == "POST":
        # version_data has all teh necessary initial data
        results = build_vers(model)
    else:
        results = {"status": "No action taken"}
    return render(request, "model_version_initial.html", {"results": results})
