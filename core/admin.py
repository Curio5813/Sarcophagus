from django.contrib import admin
from .models import Games, Membro, GameRating


@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ('game', 'ativo', 'modificado')


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('membro', 'ativo', 'modificado')


@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('membro', 'game', 'rating', 'favorito')
    list_filter = ('favorito', 'rating')
    search_fields = ('membro__membro', 'game__game')


