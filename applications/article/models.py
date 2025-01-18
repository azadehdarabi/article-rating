from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from utilities.base_models import BaseModel


class Article(BaseModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    content = models.TextField(verbose_name=_("Content"))
    rating_count = models.PositiveIntegerField(verbose_name=_("Rating Count"), default=0)
    average_rating = models.FloatField(verbose_name=_("Average Rating"), default=0.0)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    def __str__(self):
        return self.title


class UserArticleRate(BaseModel):
    user = models.ForeignKey(verbose_name=_("User"), to=User, on_delete=models.CASCADE, db_index=True)
    article = models.ForeignKey(verbose_name=_("Article"), to=Article, on_delete=models.CASCADE,
                                related_name=_("ratings"), db_index=True)
    rate = models.PositiveSmallIntegerField(verbose_name=_("Rate"))

    class Meta:
        verbose_name = _("User Article Rate")
        verbose_name_plural = _("Users Article Rate")
        unique_together = ('user', 'article')

    def __str__(self):
        return f'{self.user.username} - {self.article.title} - {self.rate}'
