import logging

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError, IntegrityError


logger = logging.getLogger(__name__)


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户管理'

    def ready(self):
        self._ensure_default_admin_exists()

    @staticmethod
    def _ensure_default_admin_exists():
        """确保默认管理员账号存在，便于前端自动登录使用。"""
        User = get_user_model()
        username = getattr(settings, 'DEFAULT_ADMIN_USERNAME', 'admin')
        password = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'admin234')
        email = getattr(settings, 'DEFAULT_ADMIN_EMAIL', 'admin@python100days.com')

        try:
            if User.objects.filter(username=username).exists():
                return
            User.objects.create_superuser(username=username, password=password, email=email)
            logger.info('默认管理员账户 %s 已创建。', username)
        except (OperationalError, ProgrammingError):
            # 在迁移或数据库尚未准备好时静默跳过，避免阻断启动流程
            logger.debug('数据库未就绪，跳过默认管理员账户检查。')
        except IntegrityError:
            logger.debug('默认管理员账户已存在，跳过创建。')
