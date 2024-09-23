from django.db import models
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


class Games(Base):
    game = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', max_length=300)
    genero = models.CharField('Genero', max_length=100)
    rating = models.DecimalField('Rating', max_digits=2, decimal_places=1)
    ano = models.IntegerField('Ano')
    desenvolvedor = models.CharField('Desenvolvedor', max_length=100)
    distribuidor = models.CharField('Distribuído', max_length=100)
    imagem = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': {'width': 560, 'height': 347, 'crop': True}})

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    def __str__(self):
        return self.game


class Membro(Base):
    first_name = models.CharField('Nome', max_length=50)
    last_name = models.CharField('Sobrenome', max_length=100)
    membro = models.CharField('Membro', max_length=100)
    email = models.EmailField('E-mail', max_length=100)
    senha = models.CharField('Senha', max_length=100)
    nascimento = models.DateField('Data de Nascimento')
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    imagem = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': {'width': 200, 'height': 200, 'crop': True}})

    class Meta:
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'

    def __str__(self):
        return self.membro

