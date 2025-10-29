from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, UserRegisterView,
    CustomTokenObtainPairView, user_stats,
    UserAdminViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('manage', UserAdminViewSet, basename='user-manage')

urlpatterns = [
    # JWT认证
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterView.as_view(), name='register'),
    
    # 用户统计
    path('users/stats/', user_stats, name='user_stats'),
    
    # 其他用户接口
    path('', include(router.urls)),
]

