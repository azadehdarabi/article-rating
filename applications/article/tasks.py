from celery import shared_task
from django.db.models import Avg
from django.utils import timezone

from .models import Article, UserArticleRate


@shared_task(name='update_article_rating')
def update_article_rating():
    updates = []
    now = timezone.now()

    articles = Article.objects.all()

    for article in articles:
        article.detect_spam_scores()

        new_average_score = UserArticleRate.objects.filter(
            content=article, is_spam=False, created_time__gte=article.calculated_to
        ).aggregate(Avg('score'))['score__avg'] or 0.0

        new_score_count = UserArticleRate.objects.filter(
            content=article, is_spam=False, created_time__gte=article.calculated_to).count()

        updated_score_count = article.rating_count + new_score_count

        if updated_score_count > 0:
            updated_average_score = ((article.average_rating * article.rating_count) + (
                    new_average_score * new_score_count)) / updated_score_count

        else:
            updated_average_score = 0.0

        updates.append(Article(
            id=article.id,
            average_rating=updated_average_score,
            rating_count=updated_score_count,
            calculated_to=now
        ))

    if updates:
        Article.objects.bulk_update(updates, ['average_rating', 'rating_count', 'calculated_to'])
