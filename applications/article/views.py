from django.db.models import OuterRef, Subquery, IntegerField
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utilities.paginator import ResponsePaginator
from .models import Article, Rating
from .serializers import RateArticleSerializer, ArticleListSerializer
from .tasks import update_article_rating


class ArticleListView(generics.GenericAPIView):
    queryset = Article.objects.filter(is_active=True)
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ResponsePaginator()

    def get(self, request):
        user = self.request.user

        user_rating = Rating.objects.filter(
            user=user,
            article=OuterRef('pk')
        ).values('rate')[:1]

        result = self.queryset.annotate(user_rating=Subquery(user_rating[:1]))

        result = self.pagination_class.paginate_queryset(request=self.request, queryset=result)
        return self.pagination_class.get_paginated_response(self.serializer_class(result, many=True).data)


class RateArticleView(generics.GenericAPIView):
    queryset = Article.objects.filter(is_active=True)
    serializer_class = RateArticleSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'article_uuid'
    lookup_field = 'uuid'

    def post(self, request, article_uuid):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        rate = serializer.validated_data['rate']

        user = self.request.user
        article = self.get_object()

        Rating.objects.update_or_create(user=user, article=article, defaults={'rate': rate})
        update_article_rating.delay(article.id)

        return Response({"message": "Rating recorded successfully"}, status=status.HTTP_200_OK)
