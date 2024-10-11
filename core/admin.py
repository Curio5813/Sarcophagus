from django import forms
from django.contrib import admin
from .models import Games, Membro, GameRating, Genero


class MembroForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False)

    class Meta:
        model = Membro
        fields = '__all__'  # ou especifique os campos que deseja incluir

    def save(self, commit=True):
        membro = super().save(commit=False)
        if self.cleaned_data['password']:  # Verifica se a senha foi fornecida
            membro.set_password(self.cleaned_data['password'])  # Criptografa a senha
        if commit:
            membro.save()  # Salva o membro
        return membro

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ('game', 'ativo', 'modificado')
    filter_horizontal = ('generos',)

@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    form = MembroForm  # Use o formulário personalizado
    list_display = ('membro', 'ativo', 'modificado')

@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('membro', 'game', 'rating', 'favorito')
    list_filter = ('favorito', 'rating')
    search_fields = ('membro__membro', 'game__game')
