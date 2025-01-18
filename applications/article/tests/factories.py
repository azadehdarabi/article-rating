import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory

from applications.article.models import Article, UserArticleRate


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')


class ArticleFactory(DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Sequence(lambda n: f"title_{n}")
    content = factory.Sequence(lambda n: f"content_{n}")


class UserArticleRateFactory(DjangoModelFactory):
    class Meta:
        model = UserArticleRate

    user = factory.SubFactory(UserFactory)
    article = factory.SubFactory(ArticleFactory)
    rate = factory.Sequence(lambda n: n % 5 + 1)
