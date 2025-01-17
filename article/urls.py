from rest_framework.routers import DefaultRouter
from .views import RateArticleViewSet

router = DefaultRouter()
router.register('article', RateArticleViewSet, basename='article')

urlpatterns = router.urls
