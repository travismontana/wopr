from django.db import models
import uuid


class ModelFamily(models.Model):
    """e.g. yolo11m"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mf_status = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        db_table = "model_families"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["name"]),
            models.Index(fields=["shortname"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        verbose_name_plural = "Model Families"

    def __str__(self):
        return self.name


class ModelInfo(models.Model):
    """Model"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    family = models.ForeignKey(
        ModelFamily, on_delete=models.CASCADE, related_name="models"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "model_info"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["name"]),
            models.Index(fields=["shortname"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["family"]),  # ADDED: FK index for query performance
        ]
        verbose_name_plural = "Model Info"

    def __str__(self):
        return self.name


class ModelVersion(models.Model):
    """Info about each version"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    version = models.IntegerField()
    artifact_uri = models.CharField(max_length=1024)
    checksum = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    trained_at = models.DateTimeField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    model = models.ForeignKey(
        ModelInfo, on_delete=models.CASCADE, related_name="versions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "model_version"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["version"]),
            models.Index(fields=["is_current"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["model"]),  # ADDED: FK index for query performance
        ]
        verbose_name_plural = "Model Versions"

    def __str__(self):
        return f"{self.model.name} v{self.version}"


class ModelBackup(models.Model):
    """Backup info of the model"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    taken_at = models.DateTimeField()
    was_successful = models.BooleanField(default=False)
    artifact_uri = models.CharField(max_length=1024, unique=True)
    model_version = models.ForeignKey(
        ModelVersion, on_delete=models.CASCADE, related_name="backups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "model_backup"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["taken_at"]),
            models.Index(fields=["was_successful"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(
                fields=["model_version"]
            ),  # ADDED: FK index for query performance
        ]
        verbose_name_plural = "Model Backups"

    def __str__(self):
        return f"Backup for {self.model_version} at {self.taken_at}"


class Dataset(models.Model):
    """Dataset artifact storage"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    artifact_uri = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "datasets"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        verbose_name_plural = "Datasets"

    def __str__(self):
        return f"Dataset {self.uuid}"


class Result(models.Model):
    """Training run results and metrics"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    accuracy = models.FloatField(blank=True, null=True)
    loss = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    artifact_uri = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "results"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        verbose_name_plural = "Results"

    def __str__(self):
        return f"Result {self.uuid} - Acc: {self.accuracy}, Loss: {self.loss}"


class TrainingRun(models.Model):
    """Training run orchestration linking datasets, models, and results"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    training_parameters = models.JSONField(blank=True, null=True, default=dict)
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="training_runs"
    )
    result = models.ForeignKey(
        Result,
        on_delete=models.SET_NULL,
        related_name="training_runs",
        blank=True,
        null=True,
    )
    model_version = models.ForeignKey(
        ModelVersion, on_delete=models.CASCADE, related_name="training_runs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    run_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "training_run"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["dataset"]),
            models.Index(fields=["result"]),
            models.Index(fields=["model_version"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["run_timestamp"]),
        ]
        verbose_name_plural = "Training Runs"

    def __str__(self):
        return f"TrainingRun {self.uuid} - {self.run_timestamp}"
