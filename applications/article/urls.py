from django.urls import path
from .views import RateArticleView, ArticleListView

urlpatterns = [
    path('list', ArticleListView.as_view(), name='article-list'),
    path('rate_article/<str:article_uuid>/', RateArticleView.as_view(), name='article-rate'),
]
