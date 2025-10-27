from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

from .serializers import (
    UserSerializer, UserRegisterSerializer,
    CustomTokenObtainPairSerializer, UserProfileSerializer
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
