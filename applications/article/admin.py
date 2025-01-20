from django.contrib import admin
from .models import Article, UserArticleRate


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating_count', 'average_rating', 'last_calculation')
    search_fields = ('title',)
    readonly_fields = ('uuid', 'created_time', 'updated_time', 'last_calculation')


@admin.register(UserArticleRate)
class UserArticleRateAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'rate')
    list_filter = ('is_spam', 'rate', 'created_time')
    search_fields = ('user__username', 'article__title')
    readonly_fields = ('uuid', 'created_time', 'updated_time')
