from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (HomeView, GameView, CommunityView, ContactView,
                    ReviewView, AvaliarJogoView, FavoritarJogoView,
                    GameSearchView, BlogView, TesteView, LoginView,
                    RegisterView, GameDetailView, MembroDetailView, BlogPostEditView,
                    MembroEditView, autocomplete_games, logout_view)
from .views import BlogPostCreateView, BlogPostDetailView, TournamentDetailView, JoinTournamentView
from django.shortcuts import redirect
from allauth.socialaccount.views import SignupView


class CustomSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        """Redireciona automaticamente usuários para a home"""
        return redirect("/")

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('game-details/', GameSearchView.as_view(), name='game-details'),
    path('game/<int:id>/', GameDetailView.as_view(), name='game-details'),
    path('games/', GameView.as_view(), name='games'),
    path('avaliar_jogo/', AvaliarJogoView.as_view(), name='avaliar_jogo'),
    path('favoritar_jogo/', FavoritarJogoView.as_view(), name='favoritar_jogo'),
    path('community/', CommunityView.as_view(), name='community'),
    path('membro/<int:id>/', MembroDetailView.as_view(), name='membro-details'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('reviews/', ReviewView.as_view(), name='reviews'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('teste/', TesteView.as_view(), name='teste'),
    path('login/', LoginView.as_view(), name='login'),  # Corrigido
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),  # Corrigido
    path('blog/create/', BlogPostCreateView.as_view(), name='blog_create'),
    path('blog/<int:pk>/', BlogPostDetailView.as_view(), name='blog_post_detail'),
    path('blog/<int:pk>/edit/', BlogPostEditView.as_view(), name='blog_post_edit'),
    path('tournament/<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournament/<int:pk>/join/', JoinTournamentView.as_view(), name='join_tournament'),
    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
    path('search/', GameSearchView.as_view(), name='game_search'),
    path('autocomplete/', autocomplete_games, name='autocomplete_games'),
    path('membro/edit/', MembroEditView.as_view(), name='membro-edit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
