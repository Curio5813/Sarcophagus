from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import ContatoForm, MembroLoginForm, BlogCommentForm
from .models import Membro, GameRating, Tournament
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.utils import translation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from django.db.models import Q
from django import forms
from django.db.models import Avg
from django.contrib.auth.decorators import user_passes_test
from .models import BlogPost, Genero, Games
from .forms import BlogForm
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView
from django.contrib import messages
from django.urls import reverse


def autocomplete_games(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        games = Games.objects.filter(game__icontains=query).values_list('game', flat=True)[:10]
        return JsonResponse(list(games), safe=False)
    return JsonResponse([], safe=False)


class HomeView(TemplateView):
    template_name = 'index/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Define a ordem de prioridade dos gêneros
        generos_prioridade = ['Shooter', 'Puzzle', 'Racing', 'Simulation']
        jogos_adicionados = []

        for genero_nome in generos_prioridade:
            jogo = Games.objects.filter(
                generos__nome=genero_nome
            ).exclude(id__in=[j.id for j in jogos_adicionados]).order_by('-criado').first()

            if jogo:
                # Garante que o gênero prioritário seja destacado
                jogo.genero_prioritario = genero_nome
                jogos_adicionados.append(jogo)

        # Completa com jogos restantes se não tiver 4
        if len(jogos_adicionados) < 4:
            jogos_restantes = Games.objects.exclude(
                id__in=[j.id for j in jogos_adicionados]
            ).order_by('-criado')[:4 - len(jogos_adicionados)]

            for jogo in jogos_restantes:
                # Define o gênero prioritário com base na ordem ou o primeiro gênero associado
                for genero_nome in generos_prioridade:
                    if genero_nome in jogo.generos.values_list('nome', flat=True):
                        jogo.genero_prioritario = genero_nome
                        break
                else:
                    # Fallback para o primeiro gênero disponível
                    jogo.genero_prioritario = jogo.generos.first().nome if jogo.generos.exists() else "Outro"
                jogos_adicionados.append(jogo)

        context['jogos_por_genero'] = jogos_adicionados

        # Adiciona o campeonato em destaque do jogo Diablo
        context['tournaments'] = Tournament.objects.all().order_by('-start_date')  # Ordena pelos mais recentes

        return context


class DownloadView(TemplateView):
    template_name = 'download/download.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        context['generos'] = Genero.objects.all()
        context['anos'] = range(1987, 2006)

        # Obter parâmetros de busca da solicitação
        game = self.request.GET.get('game')
        descricao = self.request.GET.get('descricao')
        genero = self.request.GET.get('genero', None)  # Altere para "genero" (singular)
        ano = self.request.GET.get('ano')
        desenvolvedor = self.request.GET.get('desenvolvedor')
        distribuidor = self.request.GET.get('distribuidor')

        # Inicializar o queryset como vazio
        queryset = Games.objects.none()

        # Verificar se algum campo de busca foi preenchido
        if any([game, descricao, genero, ano, desenvolvedor, distribuidor]):
            queryset = Games.objects.all().order_by('ano')
            if game:
                queryset = queryset.filter(game__icontains=game)
            if descricao:
                queryset = queryset.filter(descricao__icontains=descricao)
            if genero:
                queryset = queryset.filter(generos__id=genero)  # Filtrar pelo ID do gênero
            if ano:
                queryset = queryset.filter(ano=ano)
            if desenvolvedor:
                queryset = queryset.filter(desenvolvedor__icontains=desenvolvedor)
            if distribuidor:
                queryset = queryset.filter(distribuidor__icontains=distribuidor)

        # Se o usuário estiver logado, pegar a avaliação mais recente e favoritos
        if self.request.user.is_authenticated:
            membro = Membro.objects.get(email=self.request.user.email)

            # Buscar a última avaliação e se foi favoritado
            game_ratings = GameRating.objects.filter(membro=membro).order_by('-criado')

            # Criar um dicionário para armazenar avaliações e favoritos
            ratings_dict = {rating.game.id: rating for rating in game_ratings}

            # Adicionar informações ao contexto dos jogos
            for game in queryset:
                game.user_rating = ratings_dict.get(game.id).rating if ratings_dict.get(game.id) else None
                game.user_favorito = ratings_dict.get(game.id).favorito if ratings_dict.get(game.id) else False
        context['games'] = queryset

        return context


class CommunityView(TemplateView):
    template_name = 'community/community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            search_query = self.request.GET.get('membro', '').strip()
            post_id = self.request.GET.get('post_id')  # Novo parâmetro para filtrar por post

            # Se o parâmetro post_id estiver presente, filtra membros que comentaram no post específico
            if post_id:
                membros = Membro.objects.filter(
                    blogcomment__post_id=post_id  # Atualiza para o campo correto
                ).distinct()
                context['show_all_members_title'] = False
            else:
                # Mantém os filtros já existentes
                if self.request.user.is_superuser:
                    if search_query:
                        membros = Membro.objects.filter(
                            Q(first_name__icontains=search_query) |
                            Q(last_name__icontains=search_query) |
                            Q(membro__icontains=search_query)
                        )
                        context['show_all_members_title'] = False  # Pesquisa ativa
                    else:
                        membros = Membro.objects.all()
                        context['show_all_members_title'] = True  # Sem pesquisa
                else:
                    if search_query:
                        membros = Membro.objects.filter(
                            Q(first_name__icontains=search_query) |
                            Q(last_name__icontains=search_query) |
                            Q(membro__icontains=search_query)
                        )
                    else:
                        membros = Membro.objects.filter(id=self.request.user.id)

            context['membros'] = membros
            context['membros_count'] = membros.count()

            if membros.count() == 1:
                membro_pesquisado = membros.first()
                jogos_favoritos = GameRating.objects.filter(
                    membro=membro_pesquisado, favorito=True
                ).select_related('game')
                context['jogos_favoritos'] = jogos_favoritos

        return context


class MembroDetailView(TemplateView):
    template_name = 'membro-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membro_id = kwargs['id']
        membro = get_object_or_404(Membro, id=membro_id)
        context['membro'] = membro

        # Buscar jogos favoritos do membro
        jogos_favoritos = GameRating.objects.filter(membro=membro, favorito=True).select_related('game')
        context['jogos_favoritos'] = jogos_favoritos

        return context


class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContatoForm
    success_url = reverse_lazy('contact')

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        lang = translation.get_language()
        context['lang'] = lang
        translation.activate(lang)
        return context

    def form_valid(self, form, *args, **kwargs):
        try:
            form.send_mail()
            messages.success(self.request, 'E-mail enviado com sucesso.')
        except Exception as e:
            messages.error(self.request, f'Erro ao enviar e-mail: {str(e)}')
        return super(ContactView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        try:
            messages.success(self.request, 'E-mail enviado com sucesso.')
        except Exception as e:
            messages.error(self.request, f'Erro ao enviar e-mail: {str(e)}')
        return super(ContactView, self).form_invalid(form)


class ReviewView(TemplateView):
    template_name = 'reviews/reviews.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obter todos os jogos
        reviews = Games.objects.all().order_by('ano')

        # Verificar se o usuário está autenticado
        membro = self.request.user if self.request.user.is_authenticated else None

        # Adiciona os campos necessários para exibição
        for r in reviews:
            # Média de todas as notas
            media_rating = GameRating.objects.filter(game=r).aggregate(Avg('rating'))['rating__avg']
            review_count = GameRating.objects.filter(game=r).count()  # Número total de avaliações

            # Nota do membro logado
            user_rating = None
            if membro:
                user_rating_obj = GameRating.objects.filter(game=r, membro=membro).first()
                user_rating = user_rating_obj.rating if user_rating_obj else None

            # Se não houver média, defina como 0
            if media_rating is None:
                media_rating = 0

            # Estrelas cheias e meia estrela
            full_stars = int(media_rating // 2) + 1 # Estrelas completas
            has_half_star = (media_rating % 2) >= 0.5  # Verifica se há meia estrela

            # Atribuir valores ao objeto do jogo
            r.media_rating = media_rating
            r.review_count = review_count
            r.user_rating = user_rating
            r.full_stars = full_stars
            r.has_half_star = has_half_star

        context['reviews'] = reviews
        return context


class BlogView(TemplateView):
    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.all().order_by('-publicado_em')
        for post in posts:
            post.comment_count = post.comentarios.count()
        context['posts'] = posts
        context['latest_posts'] = posts[:3]
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            context['form'] = BlogForm()
        return context


class GameSearchView(TemplateView):
    template_name = 'game-search-results.html'  # Template para exibir os resultados

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()

        if query:
            games = Games.objects.filter(
                Q(game__icontains=query) |
                Q(descricao__icontains=query) |
                Q(gameplay__icontains=query) |
                Q(graphics__icontains=query) |
                Q(sound_and_music__icontains=query) |
                Q(conclusion__icontains=query) |
                Q(desenvolvedor__icontains=query) |
                Q(distribuidor__icontains=query) |
                Q(ano__icontains=query) |
                Q(generos__nome__icontains=query)
            ).distinct().order_by('-ano')  # Ordenar por ano

        else:
            games = Games.objects.none()

        context['games'] = games
        context['query'] = query
        return context


class GameDetailView(TemplateView):
    template_name = 'game-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs['id']
        game = get_object_or_404(Games, id=game_id)

        # Inicializa os atributos do usuário
        game.user_rating = None
        game.user_favorito = False

        if self.request.user.is_authenticated:
            try:
                membro = Membro.objects.get(email=self.request.user.email)
                game_rating = GameRating.objects.filter(membro=membro, game=game).first()
                if game_rating:
                    game.user_rating = game_rating.rating
                    game.user_favorito = game_rating.favorito
            except Membro.DoesNotExist:
                pass  # Ou lidar com exceção se necessário

        context['game'] = game
        return context


class TesteView(TemplateView):
    template_name = '404.html'


class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = MembroLoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('index')
        else:
            form.add_error(None, "Login inválido")
            return self.form_invalid(form)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    class Meta:
        model = Membro
        fields = ['email', 'first_name', 'last_name', 'membro', 'password']

    def save(self, commit=True):
        membro = super(RegisterForm, self).save(commit=False)
        membro.set_password(self.cleaned_data['password'])  # Usa o método set_password
        if commit:
            membro.save()
        return membro


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        form.save()  # Salva o novo membro
        return redirect('index')  # Redireciona para a página de login após o registro


@method_decorator(login_required, name='dispatch')
class AvaliarJogoView(TemplateView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        game_id = data.get('game_id')
        rating_value = data.get('rating')

        game = get_object_or_404(Games, id=game_id)
        membro = Membro.objects.get(email=request.user.email)

        # Verifica se já existe uma avaliação para o membro e jogo
        game_rating, created = GameRating.objects.update_or_create(
            membro=membro,
            game=game,
            defaults={'rating': rating_value}
        )

        return JsonResponse({'success': True})


class FavoritarJogoView(TemplateView):
    def post(self, request):
        data = json.loads(request.body)
        game_id = data.get('game_id')
        favorito = data.get('favorito')

        # Obtém o membro logado
        membro = Membro.objects.get(email=request.user.email)

        # Obtém o jogo
        game = Games.objects.get(id=game_id)

        # Verifica se já existe uma avaliação
        rating, created = GameRating.objects.get_or_create(membro=membro, game=game)

        # Atualiza o status de favorito
        rating.favorito = favorito
        rating.save()

        return JsonResponse({"success": True})


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class BlogPostCreateView(FormView):
    template_name = 'blog/blog_post_form.html'
    form_class = BlogForm
    success_url = reverse_lazy('blog')

    def form_valid(self, form):
        blog_post = form.save(commit=False)
        blog_post.autor = self.request.user
        blog_post.save()
        messages.success(self.request, 'Post published successfully!')
        return super().form_valid(form)


class BlogPostDetailView(TemplateView):
    template_name = 'blog/blog_post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(BlogPost, pk=kwargs['pk'])
        context['post'] = post
        context['comentarios'] = post.comentarios.all()
        context['latest_posts'] = BlogPost.objects.order_by('-publicado_em')[:3]

        # Verifique se o usuário está autenticado e não é superusuário
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            context['comment_form'] = BlogCommentForm()

        return context

    def post(self, request, *args, **kwargs):
        # Processa o envio de comentários
        post = get_object_or_404(BlogPost, pk=kwargs['pk'])
        if request.user.is_authenticated and not request.user.is_superuser:
            comment_form = BlogCommentForm(request.POST)
            if comment_form.is_valid():
                comentario = comment_form.save(commit=False)
                comentario.post = post
                comentario.membro = request.user
                comentario.save()
                messages.success(request, "Comentário enviado com sucesso!")
                return redirect('blog_post_detail', pk=post.pk)
        return self.get(request, *args, **kwargs)


class BlogPostEditView(UserPassesTestMixin, UpdateView):
    model = BlogPost
    fields = ['titulo', 'conteudo', 'imagem']  # Campos permitidos para edição
    template_name = 'blog/blog_post_form.html'  # Template para edição
    success_url = reverse_lazy('blog')  # Redireciona para a página do blog após edição

    def test_func(self):
        # Permite acesso se o usuário for o autor e um superusuário
        post = self.get_object()
        return self.request.user.is_superuser and self.request.user == post.autor


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'tournament/tournament_detail.html'
    context_object_name = 'tournament'


class JoinTournamentView(TemplateView):
    def post(self, request, pk):
        tournament = get_object_or_404(Tournament, pk=pk)
        if request.user.is_authenticated and tournament.participants.count() < tournament.max_participants:
            tournament.participants.add(request.user)
            messages.success(request, "Você foi inscrito no campeonato!")
        else:
            messages.error(request, "Não foi possível realizar a inscrição.")
        return redirect(reverse('tournament_detail', args=[pk]))
