from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContatoForm, BlogForm
from .models import Games, Membro
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _
from django.utils import translation



class HomeView(TemplateView):
    template_name = 'index/index.html'


class DownloadView(TemplateView):
    template_name = 'download/download.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        context ['membros'] = Membro.objects.all()
        return context

class CommunityView(TemplateView):
    template_name = 'community/community.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityView, self).get_context_data(**kwargs)
        context ['membros'] = Membro.objects.all()
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
        context = super(ReviewView, self).get_context_data(**kwargs)
        context ['reviews'] = Games.objects.all()
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
            games = Games.objects.filter(game__icontains=query).order_by('game')  # Filter by game name
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
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('index')
        else:
            return self.form_invalid(form)

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('index')
        else:
            return self.form_invalid(form)

class RegisterForm(FormView):

    class Meta:
        model = Membro
        field = ['username', 'email', 'password']
