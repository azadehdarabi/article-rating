from django.contrib import admin
from .models import Article, UserArticleRate


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(UserArticleRate)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'rate')
    search_fields = ('user__username', 'article__title')
    list_filter = ('rate',)
    raw_id_fields = ('user', 'article')
