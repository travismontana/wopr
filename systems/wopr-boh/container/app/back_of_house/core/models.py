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
        ]
        verbose_name_plural = "Model Info"

    def __str__(self):
        return self.name


class ModelVersion(models.Model):
    """Info about each version"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    version = models.IntegerField()
    artifact_uri = models.CharField(max_length=1024, unique=True)
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
        ]
        verbose_name_plural = "Model Versions"

    def __str__(self):
        return f"{self.model.name} v{self.version}"


class ModelStatus(models.Model):
    """Status of the model"""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    observed_at = models.DateTimeField()
    has_distfile = models.BooleanField(default=False)
    has_backup = models.BooleanField(default=False)
    model_version = models.ForeignKey(
        ModelVersion,
        on_delete=models.CASCADE,
        related_name="status_observations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "model_status"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["observed_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        verbose_name_plural = "Model Statuses"

    def __str__(self):
        return f"Status for {self.model_version} at {self.observed_at}"


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

    class Meta:
        db_table = "model_backup"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["taken_at"]),
            models.Index(fields=["was_successful"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        verbose_name_plural = "Model Backups"

    def __str__(self):
        return f"Backup for {self.model_version} at {self.taken_at}"
