from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    title = models.CharField(verbose_name="Title", max_length=255)
    content = models.TextField(verbose_name="Content")
    rating_count = models.PositiveIntegerField(verbose_name="Rating Count", default=0)
    average_rating = models.FloatField(verbose_name="Average Rating", default=0.0)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(verbose_name="User", to=User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(verbose_name="Article", to=Article, on_delete=models.CASCADE, related_name="ratings",
                                db_index=True)
    rate = models.PositiveSmallIntegerField(verbose_name="Rate")

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ('user', 'article')

    def __str__(self):
        return f'{self.user.username} - {self.article.title} - {self.rate}'
