from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContatoForm
from .models import Games, Membro


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


class TesteView(TemplateView):
    template_name = '404.html'
