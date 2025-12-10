from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from datetime import date
from cloudinary.models import CloudinaryField
import re
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import unicodedata


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
    class GenreChoices(models.TextChoices):
        Adventure = 'Adventure', _('Adventure')
        Action = 'Action', _('Action')
        Noir = 'Noir', _('Noir')
        Crime = 'Crime', _('Crime')
        RTS = 'RTS', _('Real-Time Strategy')
        TBS = 'TBS', _('Turn-Based Strategy / Tactics')
        RPG = 'RPG', _('Role-Playing Game')
        TPS = 'TPS', _('Third-Person Shooter')
        FPS = 'FPS', _('First-Person Shooter')
        Simulation = 'Simulation', _('Simulation')
        Platformer = 'Platformer', _('Platformer')
        Racing = 'Racing', _('Racing')
        War_Sim = 'War Sim', _('War Simulation / Military Strategy')
        Survival_Horror = 'Survival Horror', _('Survival Horror')
        MMORPG = 'MMORPG', _('Massively Multiplayer Online RPG')
        Sport = 'Sport', _('Sport')
        Point_and_Click = 'Point-and-Click', _('Point-and-Click')
        Puzzle = 'Puzzle', _('Puzzle')

    nome = models.CharField(_('Nome'), max_length=100, choices=GenreChoices.choices, unique=True)


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
    tempo_main_story = models.DecimalField("Main Story (h)", max_digits=5, decimal_places=2, null=True, blank=True)
    tempo_main_extras = models.DecimalField("Main + Extras (h)", max_digits=5, decimal_places=2, null=True, blank=True)
    tempo_completionist = models.DecimalField("Completionist (h)", max_digits=5, decimal_places=2, null=True, blank=True)
    tempo_all_styles = models.DecimalField("All Styles (h)", max_digits=5, decimal_places=2, null=True, blank=True)

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

    imagem = CloudinaryField('games')
    capa = CloudinaryField('games_covers', blank=True, null=True)
    video = models.URLField(_('Video URL'), blank=True, null=True)
    gog_affiliate_url = models.URLField(_('Link GOG (afiliado)'), blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # --- Conversão do vídeo YouTube para embed ---
        if self.video:
            import re
            match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{5,20})", self.video)
            if match:
                video_id = match.group(1)
                t = re.search(r"[?&]t=(\d+)", self.video)
                if t:
                    segundos = t.group(1)
                    self.video = f"https://www.youtube-nocookie.com/embed/{video_id}?start={segundos}"
                else:
                    self.video = f"https://www.youtube-nocookie.com/embed/{video_id}"

        super().save(*args, **kwargs)

        # --- Criar avaliação padrão e requisitos de sistema se for novo ---
        if is_new:
            from .models import Membro, GameRating, SystemRequirement

            # Avaliação padrão do system user
            try:
                system_user = Membro.objects.get(email='system@sarcophagus.com')
                GameRating.objects.create(
                    membro=system_user,
                    game=self,
                    rating=self.rating,
                    favorito=False
                )
            except Membro.DoesNotExist:
                print("Usuário 'system@sarcophagus.com' não encontrado. A nota inicial não foi criada.")

            # Criar requisitos de sistema se não existir
            if not hasattr(self, 'requisitos'):
                SystemRequirement.objects.create(game=self)

    def gog_affiliate_link(self):
        if self.gog_affiliate_url:
            return self.gog_affiliate_url

        base_url = "https://www.gog.com/game/"
        affiliate_id = "curio5813"
        import unicodedata

        nome = unicodedata.normalize('NFKD', self.game).encode('ASCII', 'ignore').decode('ASCII')
        nome = nome.lower().replace(' ', '_').replace("'", "").replace(":", "").replace(",", "")
        return f"{base_url}{nome}?affiliate={affiliate_id}"

    @property
    def embed_video_url(self):
        if not self.video:
            return None
        import re
        match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{5,20})", self.video)
        if not match:
            return None
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"

    def __str__(self):
        return self.game


class GameComment(models.Model):
    game = models.ForeignKey(Games, related_name='comentarios', on_delete=models.CASCADE)
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE)
    comentario = models.TextField()
    publicado_em = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='respostas', on_delete=models.CASCADE)  # 👈 Novo!
    likes = models.ManyToManyField(Membro, related_name='comentarios_curtidos', blank=True)

    def __str__(self):
        return f'{self.membro} comentou em {self.game}'


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
    imagem = CloudinaryField('blog')
    autor = models.ForeignKey(Membro, on_delete=models.CASCADE)
    publicado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    jogo = models.ForeignKey(Games, on_delete=models.CASCADE, verbose_name="Jogo relacionado")

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


class Amizade(models.Model):
    de_membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='amizades_enviadas')
    para_membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='amizades_recebidas')
    aceita = models.BooleanField(default=False)
    solicitada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('de_membro', 'para_membro')

    def __str__(self):
        return f"{self.de_membro} -> {self.para_membro} ({'Aceita' if self.aceita else 'Pendente'})"


User = get_user_model()

class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('curtida', _('Curtida')),
        ('comentario', _('Comentário')),
    ]

    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    remetente = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    comentario = models.ForeignKey('GameComment', on_delete=models.CASCADE, null=True, blank=True)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.remetente} -> {self.destinatario} ({self.tipo})"


class Seguir(models.Model):
    seguidor = models.ForeignKey(Membro, related_name='seguindo', on_delete=models.CASCADE)
    seguido = models.ForeignKey(Membro, related_name='seguidores', on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')

    def __str__(self):
        return f"{self.seguidor} segue {self.seguido}"


class Mensagem(models.Model):
    remetente = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    conteudo = models.TextField()
    enviada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-enviada_em']


class SystemRequirement(models.Model):
    game = models.OneToOneField(Games, on_delete=models.CASCADE, related_name='requisitos')

    # Campos mínimos
    so_min = models.CharField(_('SO Mínimo'), max_length=200, blank=True, null=True)
    cpu_min = models.CharField(_('CPU Mínima'), max_length=200, blank=True, null=True)
    ram_min = models.CharField(_('RAM Mínima'), max_length=100, blank=True, null=True)
    gpu_min = models.CharField(_('GPU Mínima'), max_length=200, blank=True, null=True)
    armazenamento_min = models.CharField(_('Armazenamento Mínimo'), max_length=100, blank=True, null=True)
    audio_min = models.CharField(_('Áudio Mínimo'), max_length=200, blank=True, null=True)

    # Campos recomendados
    so_rec = models.CharField(_('SO Recomendado'), max_length=200, blank=True, null=True)
    cpu_rec = models.CharField(_('CPU Recomendada'), max_length=200, blank=True, null=True)
    ram_rec = models.CharField(_('RAM Recomendada'), max_length=100, blank=True, null=True)
    gpu_rec = models.CharField(_('GPU Recomendada'), max_length=200, blank=True, null=True)
    armazenamento_rec = models.CharField(_('Armazenamento Recomendado'), max_length=100, blank=True, null=True)
    audio_rec = models.CharField(_('Áudio Recomendado'), max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Requisito de Sistema'
        verbose_name_plural = 'Requisitos de Sistema'

    def __str__(self):
        return f"Requisitos de {self.game.game}"

