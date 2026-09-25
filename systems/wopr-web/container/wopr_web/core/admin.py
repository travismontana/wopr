from django.contrib import admin

from .models import (
    Game,
    GameLabelproj,
    Image,
    ImageGame,
    MLDataset,
    Move,
    Player,
    Round,
    Session,
    SessionImage,
    SessionPlayer,
    Turn,
)

# Register your models here.
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Session)
admin.site.register(SessionImage)
admin.site.register(SessionPlayer)
admin.site.register(Image)
admin.site.register(ImageGame)
admin.site.register(Move)
admin.site.register(Round)
admin.site.register(Turn)
admin.site.register(GameLabelproj)
admin.site.register(MLDataset)
