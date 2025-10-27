from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.cache import cache
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import CourseCategory, Course, Lesson, UserProgress, UserNote
from .serializers import (
    CourseCategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    UserProgressSerializer, UserNoteSerializer
)


class CourseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """课程分类视图集"""
    queryset = CourseCategory.objects.filter(is_active=True)
    serializer_class = CourseCategorySerializer
    lookup_field = 'slug'


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """课程视图集"""
    queryset = Course.objects.filter(is_published=True).select_related('category')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count', 'like_count']
    ordering = ['order', 'id']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取课程详情(带缓存)"""
        slug = kwargs.get('slug')
        cache_key = f'course_detail_{slug}'
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # 增加浏览次数
        instance = self.get_object()
        Course.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # 缓存1小时
        cache.set(cache_key, data, 3600)
        return Response(data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """点赞课程"""
        course = self.get_object()
        Course.objects.filter(pk=course.pk).update(like_count=F('like_count') + 1)
        return Response({'status': 'success', 'like_count': course.like_count + 1})


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """课程课时视图集"""
    queryset = Lesson.objects.filter(is_published=True).select_related('course')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'content']
    ordering_fields = ['day_number', 'created_at', 'view_count']
    ordering = ['course', 'day_number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取课时详情"""
        instance = self.get_object()
        
        # 增加浏览次数
        Lesson.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """点赞课时"""
        lesson = self.get_object()
        Lesson.objects.filter(pk=lesson.pk).update(like_count=F('like_count') + 1)
        return Response({'status': 'success', 'like_count': lesson.like_count + 1})


class UserProgressViewSet(viewsets.ModelViewSet):
    """学习进度视图集"""
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'lesson__course']
    ordering = ['-last_accessed']
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related('lesson', 'lesson__course')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        """更新学习进度"""
        lesson_id = request.data.get('lesson_id')
        progress = request.data.get('progress_percentage', 0)
        study_time = request.data.get('study_time', 0)
        
        if not lesson_id:
            return Response(
                {'error': '缺少lesson_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {'error': '课时不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取或创建进度记录
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )
        
        # 更新进度
        user_progress.progress_percentage = progress
        
        # 更新学习时间(使用F表达式原子性更新)
        UserProgress.objects.filter(pk=user_progress.pk).update(
            study_time=F('study_time') + study_time
        )
        
        # 更新状态
        if progress >= 100:
            user_progress.status = 'completed'
            if not user_progress.completed_at:
                from django.utils import timezone
                user_progress.completed_at = timezone.now()
        elif progress > 0:
            user_progress.status = 'in_progress'
            if not user_progress.started_at:
                from django.utils import timezone
                user_progress.started_at = timezone.now()
        
        user_progress.save()
        
        # 重新获取以获得最新的study_time值
        user_progress.refresh_from_db()
        
        serializer = self.get_serializer(user_progress)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取学习统计数据"""
        queryset = self.get_queryset()
        total = queryset.count()
        completed = queryset.filter(status='completed').count()
        in_progress = queryset.filter(status='in_progress').count()
        total_study_time = sum(p.study_time for p in queryset)
        
        return Response({
            'total_lessons': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': total - completed - in_progress,
            'total_study_time': total_study_time,
            'completion_rate': round(completed / total * 100, 2) if total > 0 else 0
        })


class UserNoteViewSet(viewsets.ModelViewSet):
    """学习笔记视图集"""
    serializer_class = UserNoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lesson', 'is_public']
    search_fields = ['content']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 已登录用户可以看到自己的所有笔记和其他人的公开笔记
            return UserNote.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            ).select_related('user', 'lesson')
        else:
            # 未登录用户只能看公开笔记
            return UserNote.objects.filter(is_public=True).select_related('user', 'lesson')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """点赞笔记"""
        note = self.get_object()
        UserNote.objects.filter(pk=note.pk).update(like_count=F('like_count') + 1)
        return Response({'status': 'success', 'like_count': note.like_count + 1})
