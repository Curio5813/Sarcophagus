from django.contrib import admin
from django import forms
from .models import (
    Games, Membro, GameRating, Genero,
    BlogPost, Tournament, SystemRequirement
)

class MembroForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False)

    class Meta:
        model = Membro
        fields = '__all__'

    def save(self, commit=True):
        membro = super().save(commit=False)
        if self.cleaned_data['password']:
            membro.set_password(self.cleaned_data['password'])
        if commit:
            membro.save()
        return membro

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class SystemRequirementInline(admin.StackedInline):
    model = SystemRequirement
    can_delete = False
    verbose_name_plural = "Requisitos de Sistema"
    extra = 1

@admin.register(Games)
class GamesAdmin(admin.ModelAdmin):
    list_display = ('game', 'ativo', 'modificado', 'tempo_main_story', 'tempo_main_extras', 'tempo_completionist', 'tempo_all_styles')
    filter_horizontal = ('generos',)
    inlines = [SystemRequirementInline]
    readonly_fields = ('gog_affiliate_preview',)
    fields = (
        'game', 'descricao', 'gameplay', 'graphics', 'sound_and_music', 'conclusion',
        'generos', 'rating', 'ano', 'desenvolvedor', 'distribuidor',
        'imagem', 'capa', 'video',
        'ativo',
        'tempo_main_story', 'tempo_main_extras', 'tempo_completionist', 'tempo_all_styles',
        'gog_affiliate_url', 'gog_affiliate_preview'
    )

    def gog_affiliate_preview(self, obj):
        return obj.gog_affiliate_link()

    gog_affiliate_preview.short_description = "Prévia do link de afiliação"

@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    form = MembroForm
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
    search_fields = ('titulo', 'autor__membro')
    list_filter = ('publicado_em', 'autor')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_date', 'end_date', 'max_participants', 'participants_count')
    list_filter = ('game', 'start_date', 'end_date')
    search_fields = ('name', 'game__game')
    filter_horizontal = ('participants',)
    fields = ('game', 'name', 'description', 'start_date', 'end_date', 'created_by', 'participants', 'max_participants', 'capa')

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "Número de Participantes"
