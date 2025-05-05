from .models import BlogPost, BlogComment, Notificacao, Mensagem
from django.core.cache import cache
import feedparser
from .models import Amizade


def latest_posts(request):
    return {
        'latest_posts': BlogPost.objects.all().order_by('-publicado_em')[:3]
    }


def latest_comments(request):
    return {
        'latest_comments': BlogComment.objects.select_related('membro').order_by('-publicado_em')[:3]
    }


def fs_rss_feed(request):
    """
    Obtém as últimas notícias de jogos do Rock Paper Shotgun e armazena em cache.
    """
    feed_url = "https://rss.feedspot.com/folder/5hrKt2Ua4w==/rss/rsscombiner"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se já há notícias no cache
    fs_news = cache.get("fs_rss_feed")

    if not fs_news:
        feed = feedparser.parse(feed_url)
        fs_news = []

        for entry in feed.entries[:50]:
            fs_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("fs_rss_feed", fs_news, cache_timeout)

    return {"fs_news": fs_news}


def solicitacoes_pendentes_context(request):
    if request.user.is_authenticated:
        solicitacoes_pendentes = Amizade.objects.filter(
            para_membro=request.user, aceita=False
        )
    else:
        solicitacoes_pendentes = []

    return {'solicitacoes_pendentes': solicitacoes_pendentes}


def notificacoes_context(request):
    if request.user.is_authenticated:
        notificacoes_nao_lidas = Notificacao.objects.filter(destinatario=request.user, lida=False).select_related('remetente')[:5]
        return {'notificacoes_nao_lidas': notificacoes_nao_lidas}
    return {}


def mensagens_nao_lidas_context(request):
    if request.user.is_authenticated:
        mensagens_nao_lidas = Mensagem.objects.filter(destinatario=request.user, lida=False)
        return {'mensagens_nao_lidas': mensagens_nao_lidas}
    return {'mensagens_nao_lidas': []}
