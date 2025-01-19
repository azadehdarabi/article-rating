import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from applications.article.models import Article
from applications.article.tests.factories import UserFactory, ArticleFactory, UserArticleRateFactory


class ArticleTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory()

        cls.article_1 = ArticleFactory(title='article_1')
        cls.article_2 = ArticleFactory(title='article_2')
        cls.article_3 = ArticleFactory(title='article_3')

        cls.client = APIClient()

    def test_articles_list(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(reverse('article-list'))

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content.decode())
        expected_response = {
            'links': {
                'next': None,
                'previous': None
            },
            'count': 3,
            'total_pages': 1,
            'results': [{
                'uuid': str(self.article_1.uuid),
                'title': self.article_1.title,
                'rating_count': self.article_1.rating_count,
                'average_rating': self.article_1.average_rating,
                'user_rating': None
            }, {
                'uuid': str(self.article_2.uuid),
                'title': self.article_2.title,
                'rating_count': self.article_2.rating_count,
                'average_rating': self.article_2.average_rating,
                'user_rating': None
            }, {
                'uuid': str(self.article_3.uuid),
                'title': self.article_3.title,
                'rating_count': self.article_3.rating_count,
                'average_rating': self.article_3.average_rating,
                'user_rating': None
            }]
        }
        self.assertEqual(response_data, expected_response)
