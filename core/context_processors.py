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


import feedparser
from django.core.cache import cache

def gamespot_rss_feed(request):
    """
    Obtém as últimas notícias de jogos da GameSpot e armazena em cache.
    """
    feed_url = "https://www.gamespot.com/feeds/game-news/"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se o cache já tem as notícias
    gamespot_news = cache.get("gamespot_rss_feed")

    if not gamespot_news:
        feed = feedparser.parse(feed_url)
        gamespot_news = []

        for entry in feed.entries[:6]:  # Pegando as 6 notícias mais recentes
            gamespot_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("gamespot_rss_feed", gamespot_news, cache_timeout)

    return {"gamespot_news": gamespot_news}

