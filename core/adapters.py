from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect


class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Permite que usuários sejam criados automaticamente"""
        return True  # Permite novos cadastros

    def get_login_redirect_url(self, request):
        """Força o redirecionamento para a home após login"""
        return "/"

