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


def steam_rss_feed(request):
    """
    Obtém as últimas notícias de jogos do Rock Paper Shotgun e armazena em cache.
    """
    feed_url = "https://www.pcinvasion.com/feed/"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se já há notícias no cache
    steam_news = cache.get("rps_rss_feed")

    if not steam_news:
        feed = feedparser.parse(feed_url)
        steam_news = []

        for entry in feed.entries[:6]:  # Pegando as 6 notícias mais recentes
            steam_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("rps_rss_feed", steam_news, cache_timeout)

    return {"rps_news": steam_news}
