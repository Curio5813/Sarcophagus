from django.contrib.auth.backends import ModelBackend
from core.models import Membro

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Tenta buscar o usuário pelo e-mail
            user = Membro.objects.get(email=email)
            # Verifica a senha e se o membro está ativo
            if user.check_password(password) and user.is_active:
                return user
        except Membro.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Membro.objects.get(pk=user_id)
        except Membro.DoesNotExist:
            return None
