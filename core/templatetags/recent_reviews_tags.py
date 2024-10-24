from django import template
from django.db.models import Avg
from core.models import Games, GameRating


register = template.Library()

@register.inclusion_tag('recent_reviews.html')
def show_recent_reviews():
    # Buscar os últimos 3 jogos inseridos
    latest_games = Games.objects.all().order_by('-criado')[:4]

    # Calcular a média das avaliações para cada jogo
    for game in latest_games:
        media_rating = GameRating.objects.filter(game=game).aggregate(Avg('rating'))['rating__avg']
        if media_rating is None:
            media_rating = 0  # Se não houver avaliações, a média é 0

        # Atribuir ao jogo o valor da média para ser acessado no template
        game.media_rating = media_rating

    # Retornar o contexto para o template parcial
    return {'latest_games': latest_games}
