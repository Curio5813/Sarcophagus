from django.contrib import admin
from django import forms
from .models import (
    Games, Membro, GameRating, Genero,
    BlogPost, Tournament, SystemRequirement
)
import os
import re
import requests
from django.core.files.base import ContentFile
from dotenv import load_dotenv
load_dotenv()


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
    # Exibe os campos estruturados no formulário do Admin
    fields = ['game', 'descricao', 'rating', 'ano', 'desenvolvedor', 'distribuidor', 'imagem', 'capa', 'generos']

    # Torna os campos opcionais no formulário para aceitar o envio digitando apenas o nome do jogo
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in form.base_fields:
            if field_name != 'game':
                form.base_fields[field_name].required = False
        return form

    # Intercepta o salvamento e popula os campos usando a especificação estrita do RAWG
    def save_model(self, request, obj, form, change):
        # Aloca valores padrão iniciais para nunca violar as restrições do PostgreSQL
        if obj.rating is None:
            obj.rating = 0.0
        if obj.ano is None:
            obj.ano = 2000
        obj.descricao = obj.descricao or ""
        obj.desenvolvedor = obj.desenvolvedor or "Desconhecido"
        obj.distribuidor = obj.distribuidor or "Desconhecido"

        deve_buscar_api = not change or (change and (obj.rating == 0.0 or not obj.descricao))

        if deve_buscar_api and obj.game:
            api_key = os.getenv('RAWG_API_KEY', 'f5760f70de054d909fa860f26dff23d7').strip()
            match_key = re.search(r'[a-f0-9]{32}', api_key)
            if match_key:
                api_key = match_key.group(0)

            # Limpa o texto (remove anos entre parênteses para não quebrar a busca da API)
            nome_busca = re.sub(r'\s*\([^)]*\)', '', obj.game).strip()

            search_url = "https://api.rawg.io/api/games"
            payload = {'key': api_key, 'search': nome_busca}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
            }

            try:
                response = requests.get(search_url, params=payload, headers=headers, timeout=10)

                if response.status_code == 200:
                    search_data = response.json()
                    results = search_data.get('results', [])

                    # ESTRUTURA EXATA: Acessa a primeira posição da lista usando [0]
                    if results and len(results) > 0:
                        first_match = results[0]  # <-- ÍNDICE [0] RESTAURADO AQUI
                        game_id = first_match.get('id')

                        # Segunda requisição: Rota detalhada oficial (/api/games/{id})
                        detail_url = f"https://rawg.io{game_id}"
                        detail_response = requests.get(detail_url, params={'key': api_key}, headers=headers, timeout=10)

                        if detail_response.status_code == 200:
                            details = detail_response.json()

                            # Atualiza os dados principais com o retorno da API
                            obj.game = details.get('name', obj.game)

                            raw_desc = details.get('description_raw') or details.get('description', '')
                            obj.descricao = raw_desc[:1500]

                            obj.rating = float(details.get('rating') or 0.0)

                            released = details.get('released')
                            if released:
                                # Divide a data "YYYY-MM-DD" e isola a primeira posição [0] (Ano)
                                obj.ano = int(released.split('-')[0])  # <-- ÍNDICE [0] RESTAURADO AQUI

                            # ESTRUTURA EXATA: Extrai o nome do primeiro item das matrizes developers e publishers
                            devs_list = details.get('developers', [])
                            if devs_list and len(devs_list) > 0:
                                obj.desenvolvedor = devs_list[0].get('name', 'Desconhecido')  # <-- ÍNDICE [0] AQUI

                            publishers_list = details.get('publishers', [])
                            if publishers_list and len(publishers_list) > 0:
                                obj.distribuidor = publishers_list[0].get('name', 'Desconhecido')  # <-- ÍNDICE [0] AQUI

                            # Transfere a imagem da API para a memória cache local
                            bg_image_url = details.get('background_image')
                            img_content = None
                            if bg_image_url:
                                img_res = requests.get(bg_image_url, headers=headers, timeout=10)
                                if img_res.status_code == 200:
                                    img_content = img_res.content

                            rawg_genres = details.get('genres', [])

                            # Salva o registro base para disparar o seu models.py (System Requirements)
                            super().save_model(request, obj, form, change)

                            # Gravação local das imagens físicas após o ID existir no Postgres
                            if img_content:
                                try:
                                    filename_img = f"{obj.pk}_image.jpg"
                                    filename_capa = f"{obj.pk}_cover.jpg"

                                    if hasattr(obj, 'imagem') and obj.imagem is not None:
                                        obj.imagem.save(filename_img, ContentFile(img_content), save=True)
                                    if hasattr(obj, 'capa') and obj.capa is not None:
                                        obj.capa.save(filename_capa, ContentFile(img_content), save=True)
                                except Exception as img_err:
                                    print(f"⚠️ Erro ao persistir imagens locais: {img_err}")

                            # Vincula os gêneros ManyToMany baseando-se no GenreChoices
                            valid_choices = [choice for choice in Genero.GenreChoices.values]
                            generos_instancias = []

                            for g in rawg_genres:
                                rawg_genre_name = g.get('name')
                                if rawg_genre_name in valid_choices:
                                    genero_obj, created = Genero.objects.get_or_create(nome=rawg_genre_name)
                                    generos_instancias.append(genero_obj)

                            if generos_instancias:
                                obj.generos.set(generos_instancias)

                            return

            except Exception as e:
                self.message_user(request, f"Erro ao processar dados da API: {e}", level='ERROR')

        # Fallback padrão seguro para o Django Admin
        super().save_model(request, obj, form, change)

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
