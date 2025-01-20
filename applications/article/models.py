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
    last_calculation = models.DateTimeField(verbose_name=_("Last Calculation"), auto_now_add=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    def __str__(self):
        return self.title

    def detect_spam_rates(self):
        current_time = timezone.now()
        ratings_window_start = current_time - datetime.timedelta(hours=settings.RATING_TIME_WINDOW)

        recent_ratings = UserArticleRate.objects.filter(
            created_time__gte=ratings_window_start, article=self
        )

        if recent_ratings.count() < settings.MIN_VALID_RATINGS:
            return

        time_slices = self.create_time_slices(ratings_window_start)
        average_rates_per_slice = self.calculate_average_rates_per_slice(recent_ratings, time_slices)

        if not average_rates_per_slice:
            return 0
        overall_average_rate = sum(average_rates_per_slice.values()) / len(average_rates_per_slice)

        self.flag_spam_ratings(average_rates_per_slice, overall_average_rate)

    @staticmethod
    def create_time_slices(ratings_window_start):
        """
        Create time slices for the analysis period.
        """
        time_slices = []
        for i in range(0, 60 * settings.RATING_TIME_WINDOW, settings.TIME_SLICE_INTERVAL):
            slice_start = ratings_window_start + datetime.timedelta(minutes=i)
            slice_end = slice_start + datetime.timedelta(minutes=settings.TIME_SLICE_INTERVAL)
            time_slices.append((slice_start, slice_end))
        return time_slices

    @staticmethod
    def calculate_average_rates_per_slice(ratings, time_slices):
        """
        Calculate the average rate for each time slice.
        """
        average_rate = {}
        for start_time, end_time in time_slices:
            avg_score = ratings.filter(
                created_time__gte=start_time, created_time__lt=end_time
            ).aggregate(Avg('rate'))['rate__avg'] or 0.0
            average_rate[(start_time, end_time)] = avg_score
        return average_rate

    @staticmethod
    def flag_spam_ratings(average_rates, overall_average_rate):
        """
        Flag ratings as spam if their average rate significantly deviates from the overall average.
        """
        for (start_time, end_time), avg_rate in average_rates.items():
            if avg_rate > 0 and (avg_rate / overall_average_rate) > settings.SPAM_RATE_THRESHOLD:
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
