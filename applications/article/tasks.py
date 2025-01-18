from celery import shared_task
from django.db.models import Avg, Count

from .models import Article, Rating


@shared_task(name='update_article_rating')
def update_article_rating(article_id):
    aggregate_data = Rating.objects.filter(article_id=article_id).aggregate(
        avg=Avg('rate'),
        count=Count('rate')
    )
    Article.objects.filter(id=article_id).update(
        average_rating=aggregate_data['avg'] or 0,
        rating_count=aggregate_data['count'] or 0
    )
