import uuid
from django.conf import settings  # Importa as configurações para usar DEFAULT_FILE_STORAGE
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import Group, Permission, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from datetime import date

def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename

class Base(models.Model):
    criado = models.DateField(_('Created'), auto_now_add=True)
    modificado = models.DateField(_("Updating"), auto_now=True)
    ativo = models.BooleanField(_('Ativo?'), default=True)

    class Meta:
        abstract = True

class MembroManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("O campo Email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Membro(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('Nome'), max_length=50)
    last_name = models.CharField(_('Sobrenome'), max_length=100)
    membro = models.CharField(_('Membro'), max_length=16)
    email = models.EmailField(_('E-mail'), unique=True, max_length=100)
    nascimento = models.DateField(_('Data de Nascimento'), null=True, blank=True)
    bio = models.TextField(_('Bio'), max_length=500, blank=True, null=True)
    GENERO_CHOICES = [
        ('M', _('Masculino')),
        ('F', _('Feminino')),
        ('O', _('Outro')),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    # Força o uso do DEFAULT_FILE_STORAGE (S3)
    imagem = models.ImageField(_('Imagem'), upload_to=get_file_path,
                               storage=settings.DEFAULT_FILE_STORAGE,
                               blank=True, null=True)
    ativo = models.BooleanField(default=True)
    modificado = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name='membro_set',
        blank=True,
        help_text=_('Os grupos aos quais o usuário pertence.'),
        verbose_name=_('grupos')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='membro_permissions_set',
        blank=True,
        help_text=_('As permissões específicas para este usuário.'),
        verbose_name=_('permissões do usuário')
    )

    objects = MembroManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def idade(self):
        if self.nascimento:
            hoje = date.today()
            idade = hoje.year - self.nascimento.year
            if (hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day):
                idade -= 1
            return idade
        return None

    class Meta:
        verbose_name = _('Membro')
        verbose_name_plural = _('Membros')

    def __str__(self):
        return self.membro

class Genero(models.Model):
    GENERO_CHOICES = [
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Puzzle', 'Puzzle'),
        ('Racing', 'Racing'),
        ('RPG', 'RPG'),
        ('Shooter', 'Shooter'),
        ('Simulation', 'Simulation'),
        ('Sports', 'Sports'),
        ('Strategy', 'Strategy'),
    ]
    nome = models.CharField(_('Nome'), max_length=100, choices=GENERO_CHOICES, unique=True)

    class Meta:
        verbose_name = _('Gênero')
        verbose_name_plural = _('Gêneros')

    def __str__(self):
        return self.nome

class Games(Base):
    game = models.CharField(_('Nome'), max_length=100)
    descricao = models.TextField(_('Descrição'), max_length=1500)
    gameplay = models.TextField(_('Gameplay'), max_length=1500, blank=True, null=True)
    graphics = models.TextField(_('Graphics'), max_length=1500, blank=True, null=True)
    sound_and_music = models.TextField(_('Sound and Music'), max_length=1500, blank=True, null=True)
    conclusion = models.TextField(_('Conclusion'), max_length=1500, blank=True, null=True)
    generos = models.ManyToManyField(Genero, verbose_name=_('Gêneros'))
    rating = models.DecimalField(
        _('Rating'),
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    ano = models.IntegerField(_('Ano'))
    desenvolvedor = models.CharField(_('Desenvolvedor'), max_length=100)
    distribuidor = models.CharField(_('Distribuído'), max_length=100)
    # Campos de imagem usando o DEFAULT_FILE_STORAGE (S3)
    imagem = models.ImageField(_('Imagem'), upload_to=get_file_path,
                               storage=settings.DEFAULT_FILE_STORAGE)
    capa = models.ImageField(_('Capa'), upload_to=get_file_path,
                             storage=settings.DEFAULT_FILE_STORAGE,
                             blank=True, null=True)
    video = models.URLField(_('Video URL'), blank=True, null=True)

    @property
    def video_embed_url(self):
        if self.video:
            return self.video.replace("watch?v=", "embed/")
        return None

    class Meta:
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def __str__(self):
        return self.game

class GameRating(Base):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    rating = models.DecimalField(_('Nota'), max_digits=3, decimal_places=1,
                                   validators=[MinValueValidator(0), MaxValueValidator(10)])
    favorito = models.BooleanField(_('Favorito?'), default=False)

    class Meta:
        verbose_name = _('Avaliação de Jogo')
        verbose_name_plural = _('Avaliações de Jogos')
        unique_together = ('membro', 'game')

    def __str__(self):
        return f'{self.membro} - {self.game} - Nota: {self.rating}'

class BlogPost(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    # Campo de imagem para blog, usando S3
    imagem = models.ImageField(_('Imagem'), upload_to='img/blog',
                               storage=settings.DEFAULT_FILE_STORAGE)
    autor = models.ForeignKey(Membro, on_delete=models.CASCADE)
    publicado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, related_name='comentarios', on_delete=models.CASCADE)
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE)
    comentario = models.TextField()
    publicado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentário por {self.membro} no post {self.post}'

class Tournament(models.Model):
    game = models.ForeignKey('Games', on_delete=models.CASCADE, verbose_name="Jogo")
    name = models.CharField(max_length=200, verbose_name="Nome do Campeonato")
    description = models.TextField(verbose_name="Descrição")
    start_date = models.DateTimeField(verbose_name="Data de Início")
    end_date = models.DateTimeField(verbose_name="Data de Término")
    created_by = models.ForeignKey('Membro', on_delete=models.CASCADE, verbose_name="Criado por")
    participants = models.ManyToManyField(
        'Membro',
        related_name='tournaments',
        blank=True,
        verbose_name="Participantes"
    )
    max_participants = models.IntegerField(
        default=16,
        verbose_name="Máximo de Participantes",
        help_text="Número máximo de participantes permitidos."
    )
    # Campo de capa para torneio, usando S3
    capa = models.ImageField(
        upload_to='tournaments/capas/',
        verbose_name="Capa do Campeonato",
        storage=settings.DEFAULT_FILE_STORAGE,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new and self.participants.count() > self.max_participants:
            raise ValidationError(
                f"O número de participantes ({self.participants.count()}) excede o limite permitido ({self.max_participants})."
            )

    def __str__(self):
        return f"{self.name} - {self.game.game}"

    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"
        ordering = ['start_date']
