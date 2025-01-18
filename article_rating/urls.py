from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('applications.user.urls'), name='user'),
    path('api/article/', include('applications.article.urls'), name='article'),
]
