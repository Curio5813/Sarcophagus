from .models import BlogPost, BlogComment
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
    Obtém as últimas notícias do feed RSS da Steam.
    """
    feed_url = "https://store.steampowered.com/feeds/news.xml"
    feed = feedparser.parse(feed_url)

    # Pegar os 5 primeiros posts
    steam_news = []
    for entry in feed.entries[:5]:
        steam_news.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary,
        })

    return {"steam_news": steam_news}
