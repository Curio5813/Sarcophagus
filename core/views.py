from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from .forms import ContatoForm, MembroLoginForm, BlogCommentForm, GameCommentForm
from .models import Membro, GameRating, Tournament, Notificacao, Seguir, Mensagem
from django.shortcuts import redirect
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
from .models import BlogPost, Genero, Games, GameComment
from .forms import BlogForm
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from .models import Amizade
from django.views import View
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.views.decorators.http import require_POST
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError


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

        generos_prioridade = ['FPS', 'Puzzle', 'Racing', 'Simulation']
        jogos_adicionados = []

        for genero_nome in generos_prioridade:
            jogo = Games.objects.filter(
                generos__nome=genero_nome
            ).exclude(id__in=[j.id for j in jogos_adicionados]).order_by('-criado').first()

            if jogo:
                jogo.genero_prioritario = genero_nome
                jogos_adicionados.append(jogo)

        context['jogos_por_genero'] = jogos_adicionados
        context['tournaments'] = Tournament.objects.all().order_by('-start_date')  # Ordena pelos mais recentes

        try:
            slider_response = cloudinary.api.resources(
                type="upload",
                prefix="slider-",  # <- pega arquivos com nome começando por "slider-"
                resource_type="image",
                max_results=20
            )
            slider_images = [img['secure_url'] for img in slider_response['resources']]
        except CloudinaryError:
            slider_images = []

        context['slider_images'] = slider_images

        return context


class GameView(TemplateView):
    template_name = 'download/download.html'

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
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
                        ).exclude(membro='system')
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
                        ).exclude(membro='system')
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

        # Amigos (amizades aceitas)
        amigos = Amizade.objects.filter(
            Q(de_membro=membro) | Q(para_membro=membro),
            aceita=True
        ).select_related('de_membro', 'para_membro')[:12]

        lista_amigos = [
            a.para_membro if a.de_membro == membro else a.de_membro for a in amigos
        ]
        context['amigos'] = lista_amigos

        # Verificar status de amizade com o membro logado
        user = self.request.user
        if user.is_authenticated and user != membro:
            amizade = Amizade.objects.filter(
                Q(de_membro=user, para_membro=membro) |
                Q(de_membro=membro, para_membro=user)
            ).first()
            context['amizade'] = amizade

        # Buscar jogos favoritos do membro
        jogos_favoritos = GameRating.objects.filter(membro=membro, favorito=True).select_related('game')
        context['jogos_favoritos'] = jogos_favoritos

        seguindo = Membro.objects.filter(seguidores__seguidor=membro)
        seguidores = Membro.objects.filter(seguindo__seguido=membro)
        context['seguindo'] = seguindo
        context['seguidores'] = seguidores
        context['total_seguindo'] = seguindo.count()
        context['total_seguidores'] = seguidores.count()
        context['seguindo'] = seguindo

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
                media_rating = r.rating

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
            post.all_comments = post.comentarios.order_by('-publicado_em')
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
        genero_param = self.request.GET.get('genero', '').strip()

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
        elif genero_param:
            games = Games.objects.filter(
                generos__nome=genero_param
            ).distinct().order_by('-ano')
        else:
            games = Games.objects.none()

        context['games'] = games
        context['query'] = query
        context['genero_selecionado'] = genero_param
        return context


class GameDetailView(TemplateView):
    template_name = 'game-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs['id']
        game = get_object_or_404(Games, id=game_id)

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
                pass

        context['game'] = game
        context['comentarios'] = game.comentarios.filter(parent__isnull=True).select_related('membro').order_by(
            '-publicado_em')
        context['comment_form'] = GameCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                comentario_texto = data.get('comentario')
                game_id = kwargs.get('id')
                membro = request.user

                if comentario_texto and membro.is_authenticated:
                    game = get_object_or_404(Games, id=game_id)
                    comentario = GameComment.objects.create(
                        game=game,
                        membro=membro,
                        comentario=comentario_texto
                    )
                    return JsonResponse({
                        'success': True,
                        'id': comentario.id,
                        'membro': comentario.membro.membro,
                        'comentario': comentario.comentario,
                        'tempo': "Agora mesmo",
                        'membro_url': reverse('membro-details', args=[comentario.membro.id])
                    })
            except Exception as e:
                print(f"Erro no envio de comentário: {e}")
        return JsonResponse({'success': False})


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
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        membro_name = self.cleaned_data['membro']
        password = self.cleaned_data['password']

        user = Membro.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            membro=membro_name,
            password=password
        )

        return user


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Conta criada com sucesso! Bem-vindo(a), %s." % user.membro)
        return redirect('index')

    def form_invalid(self, form):
        messages.error(self.request, "Ocorreu um erro no registro. Verifique os dados e tente novamente.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)  # Termina a sessão
    return redirect('login')  # Redireciona para login


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
        context['comentarios'] = post.comentarios.order_by('-publicado_em')
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
    form_class = BlogForm  # Use o formulário completo com o campo "jogo"
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


class MembroEditView(LoginRequiredMixin, UpdateView):
    model = Membro
    fields = ['first_name', 'last_name', 'membro', 'bio', 'imagem', 'genero', 'nascimento']
    template_name = 'membro-edit.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return self.request.user  # só permite editar o próprio perfil


class SolicitarAmizadeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        para_id = kwargs.get('id')
        de_membro = request.user
        para_membro = get_object_or_404(Membro, id=para_id)

        if de_membro != para_membro:
            Amizade.objects.get_or_create(de_membro=de_membro, para_membro=para_membro)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'mensagem': 'Solicitação enviada com sucesso!'})
        else:
            return HttpResponseRedirect(reverse('membro-details', args=[para_id]))


class AceitarAmizadeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        amizade_id = kwargs.get('amizade_id')
        amizade = get_object_or_404(Amizade, id=amizade_id, para_membro=request.user)
        amizade.aceita = True
        amizade.save()
        return HttpResponseRedirect(reverse('membro-details', args=[request.user.id]))


class SolicitacoesPendentesView(LoginRequiredMixin, ListView):
    model = Amizade
    template_name = 'amizade/solicitacoes_pendentes.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        return Amizade.objects.filter(para_membro=self.request.user, aceita=False).select_related('de_membro')


@login_required
def curtir_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id)
    if request.user in comentario.likes.all():
        comentario.likes.remove(request.user)
    else:
        comentario.likes.add(request.user)
    return JsonResponse({'success': True, 'likes': comentario.likes.count()})


@login_required
def responder_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id)
    texto = request.POST.get('comentario')
    if texto:
        resposta = GameComment.objects.create(
            membro=request.user,
            game=comentario.game,
            comentario=texto,
            parent=comentario
        )
        return JsonResponse({
            'success': True,
            'id': resposta.id,
            'comentario': resposta.comentario,
            'tempo': 'Agora mesmo',
            'membro': resposta.membro.membro,  # 👈
            'parent_id': comentario.id  # 👈 Manda o ID do comentário pai
        })
    return JsonResponse({'success': False})


@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id, membro=request.user)
    novo_texto = request.POST.get('comentario')
    if novo_texto:
        comentario.comentario = novo_texto
        comentario.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id, membro=request.user)
    comentario.delete()
    return JsonResponse({'success': True})


@login_required
def curtir_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id)
    if request.user != comentario.membro:
        Notificacao.objects.get_or_create(
            destinatario=comentario.membro,
            remetente=request.user,
            tipo='curtida',
            comentario=comentario
        )

    # Alternar curtida
    if request.user in comentario.likes.all():
        comentario.likes.remove(request.user)
    else:
        comentario.likes.add(request.user)

    return JsonResponse({'success': True, 'likes': comentario.likes.count()})


@login_required
def responder_comentario(request, comentario_id):
    comentario = get_object_or_404(GameComment, id=comentario_id)
    texto = request.POST.get('comentario')

    if texto:
        resposta = GameComment.objects.create(
            membro=request.user,
            game=comentario.game,
            comentario=texto,
            parent=comentario
        )

        if comentario.membro != request.user:
            Notificacao.objects.get_or_create(
                destinatario=comentario.membro,
                remetente=request.user,
                tipo='comentario',
                comentario=comentario
            )

        return JsonResponse({
            'success': True,
            'id': resposta.id,
            'comentario': resposta.comentario,
            'tempo': 'Agora mesmo',
            'membro': resposta.membro.membro,
            'parent_id': comentario.id
        })

    return JsonResponse({'success': False})


@require_POST
@login_required
def marcar_notificacoes_lidas(request):
    Notificacao.objects.filter(destinatario=request.user, lida=False).update(lida=True)
    return JsonResponse({'success': True})


class SeguirMembroView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        seguido_id = kwargs.get('id')
        seguido = get_object_or_404(Membro, id=seguido_id)

        if request.user != seguido:
            Seguir.objects.get_or_create(seguidor=request.user, seguido=seguido)

        return JsonResponse({'seguindo': True})


class DeixarDeSeguirMembroView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        seguido_id = kwargs.get('id')
        seguido = get_object_or_404(Membro, id=seguido_id)

        Seguir.objects.filter(seguidor=request.user, seguido=seguido).delete()

        return JsonResponse({'seguindo': False})


class SeguindoListView(TemplateView):
    template_name = 'membros/seguindo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membro = get_object_or_404(Membro, id=kwargs['id'])
        seguindo = Membro.objects.filter(seguidores__seguidor=membro)
        context['membro'] = membro
        context['seguindo'] = seguindo
        return context


class SeguidoresListView(TemplateView):
    template_name = 'membros/seguidores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membro = get_object_or_404(Membro, id=kwargs['id'])
        seguidores = Membro.objects.filter(seguindo__seguido=membro)
        context['membro'] = membro
        context['seguidores'] = seguidores
        return context


class CaixaEntradaView(TemplateView):
    template_name = 'mensagens/caixa_entrada.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        remetente_id = self.request.GET.get('remetente')

        mensagens = Mensagem.objects.none()
        if remetente_id:
            mensagens = Mensagem.objects.filter(
                Q(remetente_id=remetente_id, destinatario=user) |
                Q(remetente=user, destinatario_id=remetente_id)
            ).order_by('enviada_em')

            # Marcar como lidas
            Mensagem.objects.filter(remetente_id=remetente_id, destinatario=user, lida=False).update(lida=True)

        remetentes = (
            Mensagem.objects
            .filter(destinatario=user)
            .order_by('remetente__id')  # importante: precisa ordenar pelo campo que será usado no distinct
            .distinct('remetente__id')
            .values('remetente__id', 'remetente__imagem')
        )

        context['mensagens'] = mensagens.order_by('-enviada_em')
        context['remetentes'] = remetentes
        return context


class EnviarMensagemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        destinatario_id = kwargs.get('id')
        conteudo = request.POST.get('conteudo')

        destinatario = get_object_or_404(Membro, id=destinatario_id)
        if destinatario != request.user and conteudo.strip():
            Mensagem.objects.create(remetente=request.user, destinatario=destinatario, conteudo=conteudo)
            messages.success(request, "Mensagem enviada com sucesso.")
        return redirect('membro-details', id=destinatario_id)


class DoomLauncherView(TemplateView):
    template_name = "doom_launcher.html"