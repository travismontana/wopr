from django.contrib import admin

from .models import Dataset, ModelFamily, ModelInfo, ModelVersion, Result, TrainingRun

# Register your models here.
admin.site.register(ModelFamily)
admin.site.register(ModelInfo)
admin.site.register(ModelVersion)
admin.site.register(TrainingRun)
admin.site.register(Dataset)
admin.site.register(Result)
