from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (HomeView, DownloadView, CommunityView, ContactView, ReviewView, AvaliarJogoView,
                    GameSearchView, BlogView, TesteView, LoginView, RegisterView, BlogViewForm,
                    FavoritarJogoView)

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('game-details/', GameSearchView.as_view(), name='game-details'),
    path('download/', DownloadView.as_view(), name='download'),
    path('avaliar_jogo/', AvaliarJogoView.as_view(), name='avaliar_jogo'),
    path('favoritar_jogo/', FavoritarJogoView.as_view(), name='favoritar_jogo'),
    path('community/', CommunityView.as_view(), name='community'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('reviews/', ReviewView.as_view(), name='reviews'),
    path('blog/', BlogViewForm.as_view(), name='blog'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('teste/', TesteView.as_view(), name='teste'),
    path('registration/', LoginView.as_view(), name='login'),
    path('registration/', RegisterView.as_view(), name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)