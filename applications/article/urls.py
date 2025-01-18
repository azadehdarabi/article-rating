from django.urls import path
from .views import RateArticleViewSet, ArticleListViewSet

urlpatterns = [
    path('list', ArticleListViewSet.as_view(), name='article-list'),
    path('rate_article/<str:article_uuid>/', RateArticleViewSet.as_view(), name='article-rate'),
]
