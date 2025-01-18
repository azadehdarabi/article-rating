from celery import shared_task
from math import exp
from django.utils import timezone

from .models import Article, UserArticleRate


@shared_task(name='update_article_rating')
def update_article_rating(article_id):
    ratings = UserArticleRate.objects.filter(article_id=article_id)
    weighted_sum = 0.0
    total_weight = 0.0
    lambda_decay = 0.1  # Adjust decay rate as needed

    for rating in ratings:
        time_since_rating = (timezone.now() - rating.created_time).total_seconds()
        weight = exp(-lambda_decay * time_since_rating)
        weighted_sum += rating.rate * weight
        total_weight += weight

    if total_weight > 0:
        average_rating = weighted_sum / total_weight
    else:
        average_rating = 0.0

    rating_count = ratings.count()
    Article.objects.filter(id=article_id).update(
        average_rating=average_rating,
        rating_count=rating_count
    )
