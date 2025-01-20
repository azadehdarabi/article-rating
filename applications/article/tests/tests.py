import json
import uuid
import factory

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from applications.article.models import Article, UserArticleRate
from applications.article.tests.factories import UserFactory, ArticleFactory, UserArticleRateFactory


class ArticleTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory()

        cls.article_1, cls.article_2, cls.article_3 = ArticleFactory.create_batch(3, title=factory.Iterator(
            ['article_1', 'article_2', 'article_3']))

        UserArticleRateFactory.create_batch(2, user=cls.user_1,
                                            article=factory.Iterator([cls.article_1, cls.article_2]),
                                            rate=factory.Iterator([3, 5]))

        cls.client = APIClient()

    def setUp(self):
        self.client.force_authenticate(user=self.user_1)

    def test_articles_list(self):
        response = self.client.get(reverse('article-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data['results']
        self.assertEqual(len(response_data), 3)

        for result in response_data:
            self.assertIn('user_rating', result)
            self.assertIn('title', result)
            self.assertIn('average_rating', result)
            self.assertIn('rating_count', result)

            if result['title'] == 'article_1':
                self.assertEqual(result['user_rating'], 3)
            elif result['title'] == 'article_2':
                self.assertEqual(result['user_rating'], 5)

    def test_no_articles(self):
        Article.objects.all().delete()
        response = self.client.get(reverse('article-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_article_with_no_rating(self):
        ArticleFactory(title="article_no_rating")

        response = self.client.get(reverse('article-list'))

        response_data = response.data['results']
        self.assertTrue(any(article['title'] == "article_no_rating" for article in response_data))

        article = next(article for article in response_data if article['title'] == "article_no_rating")
        self.assertIsNone(article['user_rating'])

    def test_pagination(self):
        ArticleFactory.create_batch(20)

        response = self.client.get(reverse('article-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data['links'])
        self.assertIn('previous', response.data['links'])
        self.assertIsNotNone('next', response.data['links'])


class RateArticleViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.article_1 = ArticleFactory(title='article_1')
        cls.client = APIClient()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_rate_article_first_time(self):
        url = reverse('article-rate', kwargs={'article_uuid': str(self.article_1.uuid)})

        data = {
            'rate': 4
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Rating recorded successfully")

        self.assertTrue(UserArticleRate.objects.filter(user=self.user, article=self.article_1, rate=4).exists())

    def test_update_article_rating(self):
        initial_rating = UserArticleRate.objects.create(user=self.user, article=self.article_1, rate=3)

        url = reverse('article-rate', kwargs={'article_uuid': str(self.article_1.uuid)})

        data = {
            'rate': 5
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Rating updated successfully")

        updated_rating = UserArticleRate.objects.get(id=initial_rating.id)
        self.assertEqual(updated_rating.rate, 5)

    def test_invalid_rate_value(self):
        url = reverse('article-rate', kwargs={'article_uuid': str(self.article_1.uuid)})

        data = {
            'rate': 10
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data, {'rate': ['Ensure this value is less than or equal to 5.']})

    def test_rate_article_invalid_article_uuid(self):
        url = reverse('article-rate', kwargs={'article_uuid': uuid.uuid4()})

        data = {
            'rate': 4
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data, {'detail': 'No Article matches the given query.'})
