from .models import BlogPost

def latest_posts(request):
    return {
        'latest_posts': BlogPost.objects.all().order_by('-publicado_em')[:3]
    }
