from django.db.models import OuterRef, Subquery, IntegerField
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Article, Rating
from .serializers import RateArticleSerializer, ArticleListSerializer
from .tasks import update_article_rating


class RateArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        user_rating_subquery = Rating.objects.filter(
            user=user,
            article=OuterRef('pk')
        ).values('rate')

        queryset = self.queryset.annotate(
            user_rating=Subquery(user_rating_subquery[:1], output_field=IntegerField())
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], url_path='rate', url_name='rate', detail=True,
            serializer_class=RateArticleSerializer)
    def rate_article(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        rate = serializer.validated_data['rate']

        user = self.request.user
        article = self.get_object()

        Rating.objects.update_or_create(user=user, article=article, defaults={'rate': rate})
        update_article_rating.delay(article.id)

        return Response({"message": "Rating recorded successfully"}, status=status.HTTP_200_OK)
