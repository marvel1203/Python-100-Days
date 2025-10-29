"""
创建超级管理员账号的管理命令
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = '创建超级管理员账号 admin/admin234'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin234'
        email = 'admin@python100days.com'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'用户 {username} 已存在')
            )
            return
        
        # 创建超级用户
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功创建超级管理员:\n'
                f'  用户名: {username}\n'
                f'  密码: {password}\n'
                f'  邮箱: {email}'
            )
        )
