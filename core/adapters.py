from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect


class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Impede que o Allauth peça para completar o cadastro."""
        return False  # Retorna False para impedir que a tela de cadastro apareça

    def get_login_redirect_url(self, request):
        """Força o redirecionamento para a home após login"""
        return "/"
