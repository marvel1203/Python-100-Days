from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义JWT Token序列化器"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 添加用户信息
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
        }
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    completed_lessons = serializers.SerializerMethodField()
    total_study_time = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'completed_lessons', 'total_study_time'
        ]
        read_only_fields = ['id', 'username', 'date_joined']
    
    def get_completed_lessons(self, obj):
        """获取已完成的课时数"""
        from apps.courses.models import UserProgress
        return UserProgress.objects.filter(
            user=obj,
            status='completed'
        ).count()
    
    def get_total_study_time(self, obj):
        """获取总学习时长(分钟)"""
        from apps.courses.models import UserProgress
        from django.db.models import Sum
        
        result = UserProgress.objects.filter(user=obj).aggregate(
            total=Sum('study_time')
        )
        return result['total'] or 0
