from django.shortcuts import render

from core.models import ModelInfo

from .lib.lib_training import list_all_projects


# Create your views here.
def index(request):
    models = ModelInfo.objects.all()
    projects = list_all_projects()
    context = {"models": models, "projects": projects}
    return render(request, "training.html", context)
