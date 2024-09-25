from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContatoForm, BlogForm
from .models import Games, Membro
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm



class IndexView(TemplateView):
    template_name = 'index/index.html'


class CategoriesView(TemplateView):
    template_name = 'categories/categories.html'


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


class GamesView(TemplateView):
    template_name = 'games/games.html'

    def get_context_data(self, **kwargs):
        context = super(GamesView, self).get_context_data(**kwargs)
        context ['games'] = Games.objects.all()
        return context


class BlogView(TemplateView):
    template_name = 'blog/blog.html'
    form_class = BlogForm
    success_url = reverse_lazy('blog')

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context ['membros'] = Membro.objects.all()
        return context


class BlogViewForm(FormView):
    template_name = 'blog/blog.html'
    form_class = BlogForm
    success_url = reverse_lazy('blog')

    def form_valid(self, form, *args, **kwargs):
        try:
            form.send_mail()
            messages.success(self.request, 'E-mail enviado com sucesso.')
        except Exception as e:
            messages.error(self.request, f'Erro ao enviar e-mail: {str(e)}')
        return super(BlogViewForm, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        try:
            messages.success(self.request, 'E-mail enviado com sucesso.')
        except Exception as e:
            messages.error(self.request, f'Erro ao enviar e-mail: {str(e)}')
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