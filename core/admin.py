from django.contrib import admin
from .models import Games, Membro


@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ('game', 'ativo', 'modificado')


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ('membro', 'ativo', 'modificado')

