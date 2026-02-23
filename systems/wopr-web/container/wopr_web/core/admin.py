from django.contrib import admin

from .models import (
    Game,
    Session,
    Player,
    Image,
    SessionPlayer,
    Move,
    SessionImage,
    Round,
    Turn,
    ImageGame,
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
