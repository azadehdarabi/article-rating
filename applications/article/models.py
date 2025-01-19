import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from utilities.base_models import BaseModel


class Article(BaseModel):
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
        last_content_scores = UserArticleRate.objects.filter(created_time__gte=time_from, content=self)

        if last_content_scores.count() < settings.MIN_SCORE_COUNT:
            pass

        dict_me = {}

        for i in range(0, 60 * settings.TIME_FROM_PAYLOAD, settings.TIME_FROM_SLICE):
            time_slice_start = time_from + datetime.timedelta(minutes=i)
            time_slice_end = time_slice_start + datetime.timedelta(minutes=settings.TIME_FROM_SLICE)

            time_slice = last_content_scores.filter(created_time__gte=time_slice_start, created_time__lt=time_slice_end)
            average = time_slice.aggregate(Avg('score'))['score__avg'] or 0.0

            dict_me[average] = (time_slice_start, time_slice_end)

        average_overall = sum(dict_me.keys()) / len(dict_me) if dict_me else 0

        for average, (start_time, end_time) in dict_me.items():
            if average > 0 and (average / average_overall) > settings.SPAM_RATE_THRESHOLD:
                UserArticleRate.objects.filter(created_time__gte=start_time, created_time__lt=end_time).update(
                    is_spam=True)


class UserArticleRate(BaseModel):
    user = models.ForeignKey(verbose_name=_("User"), to=User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(verbose_name=_("Article"), to=Article, on_delete=models.CASCADE,
                                related_name=_("ratings"), db_index=True)
    rate = models.PositiveSmallIntegerField(verbose_name=_("Rate"))
    is_spam = models.BooleanField(verbose_name=_("Is Spam"), default=False)

    class Meta:
        ordering = ("created_time",)
        verbose_name = _("User Article Rate")
        verbose_name_plural = _("Users Article Rate")
        unique_together = ('user', 'article')

    def __str__(self):
        return f'{self.user.username} - {self.article.title} - {self.rate}'
