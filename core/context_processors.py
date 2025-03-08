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


def fs_rss_feed(request):
    """
    Obtém as últimas notícias de jogos do Rock Paper Shotgun e armazena em cache.
    """
    feed_url = "https://rss.feedspot.com/folder/5hrKt2Ua4w==/rss/rsscombinerformat=xml"
    cache_timeout = 1800  # Cache de 30 minutos

    # Verifica se já há notícias no cache
    fs_news = cache.get("fs_rss_feed")

    if not fs_news:
        feed = feedparser.parse(feed_url)
        fs_news = []

        for entry in feed.entries[:2]:  # Pegando as 6 notícias mais recentes
            fs_news.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary,
            })

        # Armazena no cache para evitar múltiplas requisições
        cache.set("fs_rss_feed", fs_news, cache_timeout)

    return {"fs_news": fs_news}
