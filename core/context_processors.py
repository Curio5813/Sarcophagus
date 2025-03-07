from .models import BlogPost, BlogComment
from django.core.cache import cache
import feedparser


def latest_posts(request):
    return {
        'latest_posts': BlogPost.objects.all().order_by('-publicado_em')[:3]
    }


def latest_comments(request):
    return {
        'latest_comments': BlogComment.objects.select_related('membro').order_by('-publicado_em')[:3]
    }


def wpcg_rss_feed(request):
    """
    Obtém as últimas notícias de jogos do Rock Paper Shotgun e armazena em cache.
    """
    feed_url = "worldofpcgames.com/feed"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se já há notícias no cache
    wpcg_news = cache.get("wpcg_rss_feed")

    if not wpcg_news:
        feed = feedparser.parse(feed_url)
        wpcg_news = []

        for entry in feed.entries[:6]:  # Pegando as 6 notícias mais recentes
            wpcg_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("wpcg_rss_feed", wpcg_news, cache_timeout)

    return {"wpcg_news": wpcg_news}
