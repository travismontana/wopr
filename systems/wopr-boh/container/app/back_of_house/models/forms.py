from django import forms
from core.models import ModelInfo, ModelFamily, ModelVersion, ModelStatus, ModelBackup


class TrainingModelForm(forms.ModelForm):
    class Meta:
        model = ModelInfo
        fields = ["name", "shortname", "family", "description", "note"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "cols": 40}),
            "note": forms.Textarea(attrs={"rows": 3, "cols": 40})
        }

class TrainingModelFamilyForm(forms.ModelForm):
    class Meta:
        model = ModelFamily
        fields = ["name", "shortname", "url", "description", "note"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class TrainingModelVersionForm(forms.ModelForm):
    class Meta:
        model = ModelVersion
        fields = [
            "model",
            "version",
            "artifact_uri",
            "checksum",
            "description",
            "note",
            "trained_at",
            "is_current",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "note": forms.Textarea(attrs={"rows": 3}),
            "trained_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class TrainingModelStatusForm(forms.ModelForm):
    class Meta:
        model = ModelStatus
        fields = ["model_version", "observed_at", "has_distfile", "has_backup"]
        widgets = {
            "observed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class TrainingModelBackupForm(forms.ModelForm):
    class Meta:
        model = ModelBackup
        fields = ["model_version", "taken_at", "was_successful", "artifact_uri"]
        widgets = {
            "taken_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class ModelFamilyBulkForm(forms.Form):  # Plain Form - no model needed
    file = forms.FileField(
        label="Upload CSV File",
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )