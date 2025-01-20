from django.apps import AppConfig


class ArticleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.article'

    def ready(self):
        from applications.article.tasks import update_article_rating