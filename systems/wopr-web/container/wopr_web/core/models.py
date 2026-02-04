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
    """Join table for sessions and players with optional seat assignment."""

    session = models.ForeignKey("Session", on_delete=models.CASCADE, db_index=True)
    player = models.ForeignKey("Player", on_delete=models.CASCADE, db_index=True)
    seat = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "session_players"
        unique_together = [["session", "player"]]
        ordering = ["session", "seat", "player"]

    def __str__(self):
        seat_info = f" (seat {self.seat})" if self.seat is not None else ""
        return f"{self.player.handle} in {self.session.short_id}{seat_info}"


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

    class Meta:
        db_table = "image"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_id


class Move(models.Model):
    """A single move in a session, forming a linked list."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False, db_index=True
    )
    short_id = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    session = models.ForeignKey("Session", on_delete=models.CASCADE, db_index=True)
    player = models.ForeignKey("Player", on_delete=models.PROTECT, db_index=True)
    previous_move = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, db_index=True
    )
    image_at_end = models.ForeignKey(
        "Image", null=True, blank=True, on_delete=models.SET_NULL, db_index=True
    )

    class Meta:
        db_table = "move"
        ordering = ["session", "created_at"]

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = str(self.uuid)[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.handle} - {self.short_id}"
