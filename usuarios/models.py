from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from stdimage.models import StdImageField
import uuid


def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename


class Base(models.Model):
    criado = models.DateField('Created', auto_now_add=True)
    modificado = models.DateField("Updating", auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class UsuarioManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True')

        return self._create_user(email, password, **extra_fields)


class CustomUsuarios(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    phone = models.CharField('Phone', max_length=20)
    is_staff = models.BooleanField('Membro da equipe', default=True)
    usable_password = models.CharField(max_length=128, blank=True)
    nascimento = models.DateField('Data de Nascimento', default='1980-01-01')
    imagem = StdImageField('Imagem', upload_to=get_file_path, default='static/img/authors/1_1.jpg',
                           variations={'thumb': {'width': 200, 'height': 200, 'crop': True}})
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    def __str__(self):
        return self.email

    objects = UsuarioManager()
