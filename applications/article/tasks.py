from celery import shared_task
from django.db.models import Avg
from django.utils import timezone

from .models import Article, UserArticleRate


@shared_task(name='update_article_rating')
def update_article_rating():
    now = timezone.now()
    updates = []

    for article in Article.objects.all():
        article.detect_spam_rates()

        new_average_rating, new_rating_count = get_new_article_ratings(article)

        updated_average_rating, updated_rating_count = calculate_updated_rating(
            article, new_average_rating, new_rating_count
        )

        updates.append(Article(
            id=article.id,
            average_rating=updated_average_rating,
            rating_count=updated_rating_count,
            last_calculation=now
        ))

    if updates:
        Article.objects.bulk_update(updates, ['average_rating', 'rating_count', 'last_calculation'])


def get_new_article_ratings(article):
    """
    Retrieve the new average rating and count for an article, excluding spam ratings.
    """
    new_average_rating = UserArticleRate.objects.filter(
        article=article, is_spam=False, created_time__gte=article.last_calculation
    ).aggregate(Avg('rate'))['rate__avg'] or 0.0

    new_rating_count = UserArticleRate.objects.filter(
        article=article, is_spam=False, created_time__gte=article.last_calculation
    ).count()

    return new_average_rating, new_rating_count


def calculate_updated_rating(article, new_average_rating, new_rating_count):
    """
    Calculate the updated average rating and rating count for an article.
    """
    updated_rating_count = article.rating_count + new_rating_count

    if updated_rating_count > 0:
        updated_average_rating = ((article.average_rating * article.rating_count) +
                                  (new_average_rating * new_rating_count)) / updated_rating_count
    else:
        updated_average_rating = 0.0

    return updated_average_rating, updated_rating_count
