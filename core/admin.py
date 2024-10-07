from django.contrib import admin
from .models import Games, Membro, GameRating, Genero


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    # O admin será capaz de adicionar novos gêneros, mas limitados às escolhas predefinidas


@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ('game', 'ativo', 'modificado')
    filter_horizontal = ('generos',)  # Para selecionar múltiplos gêneros no admin


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('membro', 'ativo', 'modificado')


@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('membro', 'game', 'rating', 'favorito')
    list_filter = ('favorito', 'rating')
    search_fields = ('membro__membro', 'game__game')


