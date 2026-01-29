from django.contrib import admin

from .models import ModelFamily
from .models import ModelInfo
from .models import ModelVersion
from .models import ModelStatus

# Register your models here.
admin.site.register(ModelFamily)
admin.site.register(ModelInfo)
admin.site.register(ModelVersion)
admin.site.register(ModelStatus)