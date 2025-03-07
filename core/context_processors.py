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


def pcgn_rss_feed(request):
    """
    Obtém as últimas notícias de jogos do Rock Paper Shotgun e armazena em cache.
    """
    feed_url = "https://pcgamesn.com/mainrss.xml"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se já há notícias no cache
    pcgn_news = cache.get("pcgn_rss_feed")

    if not pcgn_news:
        feed = feedparser.parse(feed_url)
        pcgn_news = []

        for entry in feed.entries[:6]:  # Pegando as 6 notícias mais recentes
            pcgn_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("pcgn_rss_feed", pcgn_news, cache_timeout)

    return {"pcgn_news": pcgn_news}
