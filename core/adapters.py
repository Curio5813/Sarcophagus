from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect


class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Impede que o Allauth exija um novo cadastro"""
        return False  # Bloqueia o formulário de cadastro

    def get_login_redirect_url(self, request):
        """Redireciona para a home após o login"""
        return "/"

    def pre_social_login(self, request, sociallogin):
        """Impede a tela de cadastro para usuários novos"""
        if not sociallogin.is_existing:
            return redirect("/")  # Se não for um usuário existente, manda para a home


