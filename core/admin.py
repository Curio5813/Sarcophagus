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
    fields = ['game', 'descricao', 'rating', 'ano', 'desenvolvedor', 'distribuidor', 'imagem', 'capa', 'generos']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in form.base_fields:
            if field_name != 'game':
                form.base_fields[field_name].required = False
        return form

    def save_model(self, request, obj, form, change):
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

            nome_busca = re.sub(r'\s*\([^)]*\)', '', obj.game).strip()

            search_url = "https://api.rawg.io/api/games"
            payload = {
                'key': api_key,
                'search': nome_busca,
                'platforms': '4'  # Garante que os resultados possuam versão para PC
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
            }

            try:
                response = requests.get(search_url, params=payload, headers=headers, timeout=10)

                if response.status_code != 200:
                    self.message_user(request, f"Erro {response.status_code} na API. Verifique a chave.", level='ERROR')
                    super().save_model(request, obj, form, change)
                    return

                search_data = response.json()
                results = search_data.get('results', [])

                if results and len(results) > 0:
                    # Filtra por correspondência exata de nome e ordena do mais antigo para o mais recente (retrô primeiro)
                    jogos_validos = [g for g in results if g.get('name', '').lower() == nome_busca.lower()]

                    if jogos_validos:
                        jogos_validos.sort(key=lambda x: x.get('released', '9999-12-31'))
                        target_match = jogos_validos[0]
                    else:
                        target_match = results[0]

                    game_id = target_match.get('id')

                    # --- EXECUÇÃO NA URL EXATA REQUISITADA ---
                    detail_url = f"https://api.rawg.io/api/games/{game_id}"
                    detail_response = requests.get(detail_url, params={'key': api_key}, headers=headers, timeout=10)

                    if detail_response.status_code == 200:
                        details = detail_response.json()

                        obj.game = details.get('name', obj.game)
                        raw_desc = details.get('description_raw') or details.get('description', '')
                        obj.descricao = raw_desc[:1500]
                        obj.rating = float(details.get('rating') * 2 or 0.0)

                        released = details.get('released')
                        if released:
                            obj.ano = int(released.split('-')[0])

                        # ======================================================================
                        # 🛠️ FILTRO ROBUSTO NATIVO: EXTRAÇÃO DO DESENVOLVEDOR DE PC
                        # ======================================================================
                        devs = details.get('developers', [])
                        platforms_data = details.get('platforms', [])

                        # Descobre quais empresas estão associadas à plataforma PC (ID 4) no JSON detalhado
                        pc_studios = []
                        for p_node in platforms_data:
                            platform_meta = p_node.get('platform', {})
                            if platform_meta.get('id') == 4:  # Se encontrou o nó do PC
                                # Captura os metadados ou requisitos específicos de PC que listam atribuições
                                requirements = p_node.get('requirements', {})
                                break

                        # Lógica robusta de fallback: Se houver mais de um desenvolvedor na lista (ex: "SEGA", "id Software"),
                        # e o jogo nasceu no PC, o estúdio original de PC quase sempre NÃO será a publicadora de consoles.
                        # Varremos a lista e priorizamos o desenvolvedor que não seja uma marca exclusiva de hardware de console.
                        desenvolvedor_final = "Desconhecido"
                        if devs and len(devs) > 0:
                            # Se houver a id Software ou o nome original do jogo bater com o padrão de estúdios de PC
                            for d in devs:
                                name_check = d.get('name', '')
                                if len(devs) > 1 and "sega" in name_check.lower():
                                    continue  # Pula o nó de ports se houver outra opção na lista
                                desenvolvedor_final = name_check
                                break

                            # Se sobrou apenas um desenvolvedor na matriz, usa o que o RAWG determinou
                            if desenvolvedor_final == "Desconhecido":
                                desenvolvedor_final = devs[0].get('name', 'Desconhecido')

                        obj.desenvolvedor = desenvolvedor_final
                        # ======================================================================

                        # --- APLICANDO A MESMA LÓGICA EXATA PARA PUBLISHERS (DISTRIBUIDOR) ---
                        publishers = details.get('publishers', [])
                        distribuidor_final = "Desconhecido"

                        if publishers and len(publishers) > 0:
                            for p in publishers:
                                name_check_pub = p.get('name', '')
                                # Se houver mais de uma publicadora, pula empresas que apenas distribuíram ports em consoles
                                if len(publishers) > 1 and any(console in name_check_pub.lower() for console in
                                                               ["sega", "nintendo", "sony", "playstation",
                                                                "microsoft"]):
                                    continue
                                distribuidor_final = name_check_pub
                                break

                            if distribuidor_final == "Desconhecido":
                                distribuidor_final = publishers[0].get('name', 'Desconhecido')

                        obj.distribuidor = distribuidor_final
                        
                        bg_image_url = details.get('background_image')
                        if bg_image_url:
                            img_res = requests.get(bg_image_url, headers=headers, timeout=10)
                            if img_res.status_code == 200:
                                filename_img = f"{game_id}_image.jpg"
                                filename_capa = f"{game_id}_cover.jpg"
                                obj.imagem.save(filename_img, ContentFile(img_res.content), save=False)
                                obj.capa.save(filename_capa, ContentFile(img_res.content), save=False)

                        super().save_model(request, obj, form, change)

                        rawg_genres = details.get('genres', [])
                        valid_choices = [choice for choice in Genero.GenreChoices.values]

                        for g in rawg_genres:
                            rawg_genre_name = g.get('name')
                            if rawg_genre_name in valid_choices:
                                genero_obj, created = Genero.objects.get_or_create(nome=rawg_genre_name)
                                obj.generos.add(genero_obj)
                        return

            except Exception as e:
                self.message_user(request, f"Erro ao processar dados da API: {e}", level='ERROR')

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
