from django.contrib import admin

from .models import ModelFamily
from .models import ModelInfo
from .models import ModelVersion
from .models import TrainingRun
from .models import Dataset
from .models import Result

# Register your models here.
admin.site.register(ModelFamily)
admin.site.register(ModelInfo)
admin.site.register(ModelVersion)
admin.site.register(TrainingRun)
admin.site.register(Dataset)
admin.site.register(Result)
