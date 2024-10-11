from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContatoForm, BlogForm, MembroLoginForm
from .models import Games, Membro, GameRating
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.utils.translation import gettext as _
from django.utils import translation
from math import floor
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json
from django.db.models import Q
from django import forms


class HomeView(TemplateView):
    template_name = 'index/index.html'


class DownloadView(TemplateView):
    template_name = 'download/download.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)

        # Obter parâmetros de busca da solicitação
        game = self.request.GET.get('game')
        descricao = self.request.GET.get('descricao')
        genero = self.request.GET.get('generos', None)  # Alteração aqui
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
                queryset = queryset.filter(generos__nome__icontains=genero)  # Alteração aqui
            if ano:
                queryset = queryset.filter(ano=ano)
            if desenvolvedor:
                queryset = queryset.filter(desenvolvedor__icontains=desenvolvedor)
            if distribuidor:
                queryset = queryset.filter(distribuidor__icontains=distribuidor)

        context['games'] = queryset

        # Verificar se o usuário está logado
        if self.request.user.is_authenticated:
            membro = Membro.objects.get(email=self.request.user.email)
            jogos_favoritos = Games.objects.filter(gamerating__membro=membro, gamerating__favorito=True)
            context['jogos_favoritos'] = jogos_favoritos

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Você precisa estar logado para avaliar.'}, status=403)

        membro = Membro.objects.get(email=request.user.email)
        game_id = request.POST.get('game_id')
        rating = request.POST.get('rating')
        favorito = request.POST.get('favorito', 'false') == 'true'

        try:
            game = Games.objects.get(id=game_id)
            game_rating, created = GameRating.objects.get_or_create(membro=membro, game=game)

            if rating:
                game_rating.rating = rating
            game_rating.favorito = favorito
            game_rating.save()

            return JsonResponse({'success': 'Avaliação salva com sucesso!'})

        except Games.DoesNotExist:
            return JsonResponse({'error': 'Jogo não encontrado.'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CommunityView(TemplateView):
    template_name = 'community/community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém o valor da pesquisa do campo de texto
        search_query = self.request.GET.get('membro', '').strip()

        if search_query:
            # Busca membros cujo primeiro ou último nome contém a string de pesquisa
            membros = Membro.objects.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(membro__icontains=search_query) |
                Q(first_name__icontains=search_query.split()[0]) & Q(last_name__icontains=' '.join(search_query.split()[1:]))
            )
        else:
            membros = Membro.objects.all()

        context['membros'] = membros
        context['membros_count'] = membros.count()

        # Verificar se há um membro específico sendo pesquisado
        if membros.count() == 1:
            membro_pesquisado = membros.first()

            # Buscar jogos favoritados pelo membro
            jogos_favoritos = GameRating.objects.filter(membro=membro_pesquisado, favorito=True).select_related('game')
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
        # Chama o método da superclasse para obter o contexto padrão
        context = super().get_context_data(**kwargs)

        # Obtém todos os jogos, ordenados pelo rating
        reviews = Games.objects.all().order_by('-rating')

        # Adiciona um novo campo que contém a metade do rating
        for r in reviews:
            r.half_rating = float(floor(r.rating / 2))

        # Adiciona a lista de reviews ao contexto
        context['reviews'] = reviews
        return context


class BlogView(TemplateView):
    template_name = 'blog/blog.html'
    form_class = BlogForm
    success_url = reverse_lazy('blog')

    def lista_membros(request):
        membros = Membro.objects.all()
        return render(request, 'blog/blog.html', {'membros': membros})


class GameSearchView(TemplateView):
    template_name = 'game-details.html'  # Assuming this displays search results

    def get_context_data(self, **kwargs):
        context = super(GameSearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q', '')  # Get the search query from URL parameter
        if query:
            games = Games.objects.filter(game__icontains=query).order_by('-rating')  # Filter by game name
        else:
            games = Games.objects.all().order_by('game')  # Display all games if no query
        context['game'] = games  # Add games to context
        context['query'] = query  # Add search query to context (optional)
        return context

    def get(self, request, *args, **kwargs):  # Override the default GET method
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class BlogViewForm(FormView):
    template_name = 'blog/blog.html'
    form_class = BlogForm
    success_url = reverse_lazy('blog')
    lang = translation.get_language()
    translation.activate(lang)

    def form_valid(self, form, *args, **kwargs):
        try:
            form.send_mail()
            messages.success(self.request, _('E-mail enviado com sucesso.'))
        except Exception as e:
            messages.error(self.request, _(f'Erro ao enviar e-mail: {str(e)}'))
        return super(BlogViewForm, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        try:
            messages.success(self.request, _('E-mail enviado com sucesso.'))
        except Exception as e:
            messages.error(self.request, _(f'Erro ao enviar e-mail: {str(e)}'))
        return super(BlogViewForm, self).form_invalid(form)


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
