import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from utilities.base_models import BaseModel


class Article(BaseModel):
    """
        Represents an article with a title, content, and user ratings.
    """
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    content = models.TextField(verbose_name=_("Content"))
    rating_count = models.PositiveIntegerField(verbose_name=_("Rating Count"), default=0)
    average_rating = models.FloatField(verbose_name=_("Average Rating"), default=0.0)
    calculated_to = models.DateTimeField(verbose_name=_("Calculated To"), auto_now_add=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    def __str__(self):
        return self.title

    def detect_spam_rates(self):
        now = timezone.now()
        time_from = now - datetime.timedelta(hours=settings.TIME_FROM_PAYLOAD)
        last_content_scores = UserArticleRate.objects.filter(
            created_time__gte=time_from, article=self
        )

        if last_content_scores.count() < settings.MIN_SCORE_COUNT:
            return

        time_slices = []
        for i in range(0, 60 * settings.TIME_FROM_PAYLOAD, settings.TIME_FROM_SLICE):
            time_slice_start = time_from + datetime.timedelta(minutes=i)
            time_slice_end = time_slice_start + datetime.timedelta(minutes=settings.TIME_FROM_SLICE)
            time_slices.append((time_slice_start, time_slice_end))

        time_slice_avg = {}
        for start_time, end_time in time_slices:
            avg_score = last_content_scores.filter(
                created_time__gte=start_time, created_time__lt=end_time
            ).aggregate(Avg('score'))['score__avg'] or 0.0
            time_slice_avg[(start_time, end_time)] = avg_score

        if time_slice_avg:
            average_overall = sum(time_slice_avg.values()) / len(time_slice_avg)
        else:
            average_overall = 0

        for (start_time, end_time), average in time_slice_avg.items():
            if average > 0 and (average / average_overall) > settings.SPAM_RATE_THRESHOLD:
                UserArticleRate.objects.filter(
                    created_time__gte=start_time, created_time__lt=end_time
                ).update(is_spam=True)


class UserArticleRate(BaseModel):
    """
        Represents a user's rating for a specific article.
    """
    user = models.ForeignKey(verbose_name=_("User"), to=User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(verbose_name=_("Article"), to=Article, on_delete=models.CASCADE,
                                related_name=_("ratings"), db_index=True)
    rate = models.PositiveSmallIntegerField(verbose_name=_("Rate"),
                                            validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_spam = models.BooleanField(verbose_name=_("Is Spam"), default=False)

    class Meta:
        ordering = ("created_time",)
        verbose_name = _("User Article Rate")
        verbose_name_plural = _("Users Article Rate")
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'article'], name='unique_user_article_rate'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.article.title} - {self.rate}'
