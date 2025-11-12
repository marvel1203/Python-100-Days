"""
用户相关的信号处理
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """
    在数据库迁移完成后自动创建默认管理员
    """
    # 只在users应用迁移完成后执行
    if sender.name == 'apps.users':
        username = 'admin'
        password = 'admin234'
        email = 'admin@python100days.com'

        # 检查管理员是否已存在
        if not User.objects.filter(username=username).exists():
            try:
                # 创建超级用户
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                print(f"✅ 自动创建超级管理员: {username}")
            except Exception as e:
                print(f"❌ 创建管理员失败: {e}")