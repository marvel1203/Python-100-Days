from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db.models import Q

from .serializers import (
    UserSerializer, UserRegisterSerializer,
    CustomTokenObtainPairSerializer, UserProfileSerializer,
    UserAdminSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT Token获取视图"""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 普通用户只能查看自己的信息
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新用户资料"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_password or len(new_password) < 6:
            return Response(
                {'error': '新密码至少6个字符'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码修改成功'})


class UserAdminViewSet(viewsets.ModelViewSet):
    """管理员用户管理视图集 - 仅超级管理员可访问"""
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]  # 仅管理员可访问
    
    def get_queryset(self):
        # 支持搜索和过滤
        queryset = User.objects.all().order_by('-date_joined')
        
        # 搜索用户名或邮箱
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search)
            )
        
        # 按角色过滤
        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换用户激活状态"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f'用户已{"激活" if user.is_active else "禁用"}',
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        new_password = request.data.get('password', 'password123')
        user.set_password(new_password)
        user.save()
        return Response({
            'message': '密码已重置',
            'new_password': new_password
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """获取用户学习统计"""
    from apps.courses.models import UserProgress, UserNote
    
    user = request.user
    
    # 已完成课时数
    completed_count = UserProgress.objects.filter(
        user=user,
        status='completed'
    ).count()
    
    # 学习中的课时数
    in_progress_count = UserProgress.objects.filter(
        user=user,
        status='in_progress'
    ).count()
    
    # 笔记数
    notes_count = UserNote.objects.filter(user=user).count()
    
    # 最近学习的课程
    recent_lessons = UserProgress.objects.filter(
        user=user
    ).select_related('lesson', 'lesson__course').order_by('-updated_at')[:5]
    
    recent_lessons_data = [{
        'lesson_id': up.lesson.id,
        'lesson_title': up.lesson.title,
        'course_title': up.lesson.course.title,
        'progress': up.progress_percentage,
        'last_studied': up.last_accessed,
    } for up in recent_lessons]
    
    return Response({
        'completed_lessons': completed_count,
        'in_progress_lessons': in_progress_count,
        'total_notes': notes_count,
        'recent_lessons': recent_lessons_data,
    })
