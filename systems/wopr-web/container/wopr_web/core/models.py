import uuid
from django.db import models


class Game(models.Model):
    """Board game definition."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    shortname = models.CharField(max_length=64, unique=True, db_index=True)
    url = models.URLField(max_length=1024, null=True, blank=True)
    min_players = models.IntegerField()
    max_players = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "game"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shortname


class Player(models.Model):
    """Player (human) participating in sessions."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    irl_name = models.CharField(max_length=255, unique=True, db_index=True)
    handle = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "player"
        ordering = ["handle"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.handle


class Session(models.Model):
    """A play session of a specific game."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    game = models.ForeignKey("Game", on_delete=models.PROTECT, db_index=True)
    players = models.ManyToManyField("Player", through="SessionPlayer")

    class Meta:
        db_table = "session"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.game.shortname} - {self.short_id}"


class SessionPlayer(models.Model):
    """Join table for sessions and players with REQUIRED seat assignment."""

    session = models.ForeignKey("Session", on_delete=models.CASCADE, db_index=True)
    player = models.ForeignKey("Player", on_delete=models.CASCADE, db_index=True)
    seat = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "session_players"
        unique_together = [["session", "player"], ["session", "seat"]]
        ordering = ["session", "seat", "player"]

    def __str__(self):
        return f"{self.player.handle} in {self.session.short_id} (seat {self.seat})"


class SessionImage(models.Model):
    """Join table for sessions and images"""

    session = models.ForeignKey("Session", on_delete=models.CASCADE, db_index=True)
    image = models.ForeignKey("Image", on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "session_images"
        unique_together = [["session", "image"]]
        ordering = ["session", "image"]


class Image(models.Model):
    """Image artifact captured during gameplay."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    artifact_uri = models.CharField(max_length=1024, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    checksum = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    filename = models.CharField(max_length=255, null=False, blank=False, db_index=True)

    class Meta:
        db_table = "image"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_id


class ImageGame(models.Model):
    """Image to game relationship."""

    game = models.ForeignKey("Game", on_delete=models.CASCADE, db_index=True)
    image = models.ForeignKey("Image", on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "image_game"
        unique_together = [["game", "image"]]
        ordering = ["game", "image"]


class GameLabelproj(models.Model):
    """Game to label studio project relationship."""

    game = models.ForeignKey("Game", on_delete=models.CASCADE, db_index=True)
    ls_project_id = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "game_labelproj"
        unique_together = [["game", "ls_project_id"]]
        ordering = ["game", "ls_project_id"]


class Round(models.Model):
    """A round in a session, grouping multiple turns."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    session = models.ForeignKey(
        "Session", on_delete=models.CASCADE, db_index=True, null=False, blank=False
    )
    number = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "round"
        unique_together = [["session", "number"]]
        ordering = ["session", "number"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session.short_id} - Round {self.number}"


class Turn(models.Model):
    """A turn in a round - one pass through all players."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    session = models.ForeignKey(
        "Session", on_delete=models.CASCADE, db_index=True, null=False, blank=False
    )
    round = models.ForeignKey(
        "Round", on_delete=models.CASCADE, db_index=True, null=False, blank=False
    )
    number = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "turn"
        unique_together = [["round", "number"]]
        ordering = ["session", "number"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session.short_id} - Turn {self.number}"


class Move(models.Model):
    """A single player action within a turn."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    image_at_end = models.ForeignKey(
        "Image", null=True, blank=True, on_delete=models.SET_NULL, db_index=True
    )
    player = models.ForeignKey("Player", on_delete=models.PROTECT, db_index=True)
    turn = models.ForeignKey(
        "Turn", on_delete=models.CASCADE, db_index=True, null=False, blank=False
    )

    class Meta:
        db_table = "move"
        unique_together = [["turn", "player"]]
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.handle} - Turn {self.turn.number}"


class MLDataset(models.Model):
    """A dataset used for machine learning purposes."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    game = models.ForeignKey("Game", on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "ml_dataset"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.game.shortname} - {self.short_id}"


class VisionParameters(models.Model):
    """Parameters for vision models."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    parameter = models.CharField(max_length=255, null=False, blank=False)
    scope = models.CharField(max_length=255, null=False, blank=False)
    default = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    min_value = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    max_value = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    camera = models.ForeignKey(
        "Camera",
        related_name="vision_parameters",
        on_delete=models.CASCADE,
        db_index=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "vision_parameters"
        ordering = ["-created_at"]
        unique_together = [["camera", "parameter", "scope"]]

    def __str__(self):
        return f"Vision Parameters - {self.parameter}"


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    label = models.CharField(max_length=255, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    normal_resolution = models.CharField(max_length=255, null=True, blank=True)
    max_resolution = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "camera"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Camera - {self.make} {self.model}"


class CameraCapabilities(models.Model):
    """e.g. stream, snapshot, etc..."""

    camera = models.ForeignKey("Camera", on_delete=models.CASCADE, db_index=True)
    capability = models.CharField(max_length=255, null=False, blank=False)
    """path is host:port or /dev/videoX"""
    path = models.CharField(max_length=255, null=True, blank=True)
    stream_type = models.CharField(max_length=255, null=False, blank=False)
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "camera_capabilities"
        unique_together = [["camera", "capability", "stream_type"]]
        ordering = ["camera", "capability"]

    def __str__(self):
        return f"Camera Capabilities - {self.camera} - {self.capability}"


class ImageToCamera(models.Model):
    image = models.ForeignKey("Image", on_delete=models.CASCADE, db_index=True)
    camera = models.ForeignKey("Camera", on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "image_to_camera"
        unique_together = [["image", "camera"]]
        ordering = ["image", "camera"]


class SessionToCamera(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE, db_index=True)
    camera = models.ForeignKey("Camera", on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = "session_to_camera"
        unique_together = [["session", "camera"]]
        ordering = ["session", "camera"]
