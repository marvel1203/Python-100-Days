from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Python-100-Days API",
        default_version='v1',
        description="Python学习平台后端API文档",
        contact=openapi.Contact(email="admin@python100days.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/courses/', include('apps.courses.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/exercises/', include('apps.exercises.urls')),
    path('api/community/', include('apps.community.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

# 媒体文件服务 (开发环境)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 课程资源文件服务 (始终启用)
urlpatterns += static(settings.COURSE_RESOURCES_URL, document_root=settings.COURSE_RESOURCES_ROOT)
