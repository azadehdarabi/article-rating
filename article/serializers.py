from rest_framework import serializers

from article.models import Article


class RateArticleSerializer(serializers.Serializer):
    rate = serializers.IntegerField(min_value=0, max_value=5)


class ArticleListSerializer(serializers.ModelSerializer):
    user_rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'rating_count', 'average_rating', 'user_rating']
