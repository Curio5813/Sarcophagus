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
    Obtém as últimas notícias do feed RSS da Steam com cache para evitar muitas requisições.
    """
    feed_url = "https://store.steampowered.com/feeds/news.xml"

    # Define um tempo de cache (ex: 30 minutos)
    cache_timeout = 1800  # 1800 segundos = 30 minutos

    # Verifica se já temos o feed no cache
    steam_news = cache.get("steam_rss_feed")

    if not steam_news:
        feed = feedparser.parse(feed_url)
        steam_news = []

        for entry in feed.entries:  # Pega os 5 primeiros posts
            steam_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache por 30 minutos
        cache.set("steam_rss_feed", steam_news, cache_timeout)

    return {"steam_news": steam_news}
