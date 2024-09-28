from django.urls import path
from .views import (IndexView, DownloadView, CommunityView, ContactView, GamesView, GameDetailView,
                    BlogView, TesteView, LoginView, RegisterView, BlogViewForm, GamesDetailView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('download/', DownloadView.as_view(), name='download'),
    path('community/', CommunityView.as_view(), name='community'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('game_details/', GameDetailView.as_view(), name='game_details'),
    path('games/', GamesView.as_view(), name='games'),
    path('blog/', BlogViewForm.as_view(), name='blog'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('teste/', TesteView.as_view(), name='teste'),
    path('registration/', LoginView.as_view(), name='login'),
    path('registration/', RegisterView.as_view(), name='register'),
    path('details/', GamesDetailView.as_view(), name='games_detail'),
]
