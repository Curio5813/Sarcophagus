from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()

class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """Permite o cadastro automaticamente"""
        return True

    def get_login_redirect_url(self, request):
        """Redireciona para a home após o login"""
        return "/"

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Se o usuário não existir, cria automaticamente"""
        if not sociallogin.is_existing:
            user = sociallogin.user
            if not user.email:
                return redirect("/")  # Se não tiver email, redireciona

            # Se o email já existe, usa essa conta
            existing_user = User.objects.filter(email=user.email).first()
            if existing_user:
                sociallogin.connect(request, existing_user)
            else:
                user.save()  # Cria o usuário automaticamente
                sociallogin.state['process'] = 'connect'  # Conecta o social account


