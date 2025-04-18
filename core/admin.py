from django import forms
from django.contrib import admin
from .models import Games, Membro, GameRating, Genero, BlogPost, Tournament


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(membro='system')

@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('membro', 'game', 'rating', 'favorito')
    list_filter = ('favorito', 'rating')
    search_fields = ('membro__membro', 'game__game')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'publicado_em', 'atualizado_em')
    search_fields = ('titulo', 'autor__membro')  # Permite buscar pelo título ou autor
    list_filter = ('publicado_em', 'autor')  # Filtros laterais para ajudar na busca

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_date', 'end_date', 'max_participants', 'participants_count')
    list_filter = ('game', 'start_date', 'end_date')
    search_fields = ('name', 'game__game')
    filter_horizontal = ('participants',)  # Habilita seleção de múltiplos participantes no admin
    fields = ('game', 'name', 'description', 'start_date', 'end_date', 'created_by', 'participants', 'max_participants', 'capa')

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "Número de Participantes"
