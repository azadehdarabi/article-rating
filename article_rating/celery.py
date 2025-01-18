from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'article_rating.settings')

app = Celery('article_rating')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'update-article-ratings-every-10-minutes': {
        'task': 'article.tasks.update_article_rating',
        'schedule': crontab(minute='*/10'),
        'args': (),
    },
}
