from django.urls import path
from .views import (IndexView, CategoriesView, CommunityView, ContactView, GamesView,
                    BlogView, TesteView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('community/', CommunityView.as_view(), name='community'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('games/', GamesView.as_view(), name='games'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('teste/', TesteView.as_view(), name='teste'),
]
