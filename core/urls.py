from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (HomeView, GameView, CommunityView, ContactView,
                    ReviewView, AvaliarJogoView, FavoritarJogoView,
                    GameSearchView, BlogView, TesteView, LoginView,
                    RegisterView, GameDetailView, MembroDetailView, BlogPostEditView,
                    MembroEditView, autocomplete_games, logout_view,
                    SolicitarAmizadeView, AceitarAmizadeView, SolicitacoesPendentesView,
                    marcar_notificacoes_lidas, SeguirMembroView, DeixarDeSeguirMembroView,
                    SeguindoListView, SeguidoresListView)
from .views import (BlogPostCreateView, BlogPostDetailView, TournamentDetailView, JoinTournamentView,
                    curtir_comentario, responder_comentario, editar_comentario, excluir_comentario)
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
    path('solicitar/<int:id>/', SolicitarAmizadeView.as_view(), name='solicitar_amizade'),
    path('amizade/aceitar/<int:amizade_id>/', AceitarAmizadeView.as_view(), name='aceitar_amizade'),
    path('amizade/solicitacoes/', SolicitacoesPendentesView.as_view(), name='solicitacoes_pendentes'),
    path('comentario/<int:comentario_id>/curtir/', curtir_comentario, name='curtir_comentario'),
    path('comentario/<int:comentario_id>/responder/', responder_comentario, name='responder_comentario'),
    path('comentario/<int:comentario_id>/editar/', editar_comentario, name='editar_comentario'),
    path('comentario/<int:comentario_id>/excluir/', excluir_comentario, name='excluir_comentario'),
    path('notificacoes/marcar_lidas/', marcar_notificacoes_lidas, name='marcar_notificacoes_lidas'),
    path('membro/<int:id>/seguir/', SeguirMembroView.as_view(), name='seguir_membro'),
    path('membro/<int:id>/deixar_de_seguir/', DeixarDeSeguirMembroView.as_view(), name='deixar_de_seguir_membro'),
    path('membro/<int:id>/seguindo/', SeguindoListView.as_view(), name='membro_seguindo'),
    path('membro/<int:id>/seguidores/', SeguidoresListView.as_view(), name='membro_seguidores'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
