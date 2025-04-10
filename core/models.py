from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from datetime import date
from cloudinary.models import CloudinaryField
import re
import uuid


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    if isinstance(instance, Membro):
        return f"media/members/{filename}"
    elif isinstance(instance, Games):
        return f"media/games/{filename}"
    elif isinstance(instance, BlogPost):
        return f"media/blog/{filename}"
    return f"media/others/{filename}"



class Base(models.Model):
    criado = models.DateField(_('Created'), auto_now_add=True)
    modificado = models.DateField(_("Updating"), auto_now=True)
    ativo = models.BooleanField(_('Ativo?'), default=True)

    class Meta:
        abstract = True


class MembroManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, membro, password=None):
        if not email:
            raise ValueError("O campo Email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, membro=membro)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, membro, password=None):
        user = self.create_user(email, first_name, last_name, membro, password)
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

    # Armazena a imagem no Cloudinary
    imagem = CloudinaryField('members',
                             transformation=[{'width': 128, 'height': 128, 'crop': 'fill'}],
                             blank=True,
                             null=True)
    ativo = models.BooleanField(default=True)
    modificado = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MembroManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "membro"]

    @property
    def idade(self):
        """Calcula a idade do membro com base na data de nascimento."""
        if self.nascimento:
            hoje = date.today()
            return hoje.year - self.nascimento.year - (
                        (hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))
        return None  # Retorna None caso não tenha data de nascimento

    def __str__(self):
        return self.membro if self.membro else self.email


class Genero(models.Model):
    GENRE_CHOICES = [
        ('ADVENTURE', 'Adventure'),
        ('RTS', 'Real-Time Strategy'),
        ('TBS', 'Turn-Based Strategy / Tactics'),
        ('RPG', 'Role-Playing Game'),
        ('FPS', 'First-Person Shooter'),
        ('SIMULATION', 'Simulation'),
        ('PLATFORMER', 'Platformer'),
        ('RACING', 'Racing'),
        ('WAR_SIM', 'War Simulation / Military Strategy'),
        ('SURVIVAL_HORROR', 'Survival Horror'),
        ('MMORPG', 'Massively Multiplayer Online RPG'),
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
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=1,
                                 validators=[MinValueValidator(0), MaxValueValidator(10)])
    ano = models.IntegerField(_('Ano'))
    desenvolvedor = models.CharField(_('Desenvolvedor'), max_length=100)
    distribuidor = models.CharField(_('Distribuído'), max_length=100)

    # Substituindo ImageField por CloudinaryField
    imagem = CloudinaryField('games')
    capa = CloudinaryField('games_covers', blank=True, null=True)
    video = models.URLField(_('Video URL'), blank=True, null=True)

    @property
    def embed_video_url(self):
        """Converte qualquer link do YouTube para a versão embed automaticamente"""
        if self.video:
            # Expressão regular para capturar o ID do vídeo
            match = re.search(r"(?:v=|youtu\.be/|embed/|watch\?.*v=)([A-Za-z0-9_-]+)", self.video)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}"
        return None  # Retorna None se não houver vídeo

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

    # Cloudinary para imagem do post
    imagem = CloudinaryField('blog')

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

    # Cloudinary para capa do campeonato
    capa = CloudinaryField('tournament_covers', null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new and self.participants.count() > self.max_participants:
            raise ValidationError(
                f"O número de participantes ({self.participants.count()}) excede o limite permitido ({self.max_participants})."
            )

    def __str__(self):
        return f"{self.name} - {self.game.game}"
