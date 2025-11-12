"""
用户自动登录中间件
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()


class AutoAdminLoginMiddleware(MiddlewareMixin):
    """
    自动登录管理员中间件
    当访问/admin/路径时，自动登录admin用户
    """

    def process_request(self, request):
        # 只在DEBUG模式下启用自动登录
        import os
        if not os.getenv('DEBUG', 'True') == 'True':
            return

        # 只对admin路径启用自动登录
        if request.path.startswith('/admin/') and request.user.is_anonymous:
            try:
                # 尝试获取admin用户
                admin_user = User.objects.filter(username='admin').first()
                if admin_user:
                    # 手动设置用户到session
                    request.session['_auth_user_id'] = admin_user.id
                    request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
                    request.user = admin_user
                    print(f"自动登录管理员: {admin_user.username}")
            except Exception as e:
                print(f"自动登录失败: {e}")