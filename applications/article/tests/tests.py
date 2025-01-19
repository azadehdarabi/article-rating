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
