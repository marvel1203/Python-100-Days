from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.cache import cache
from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
import uuid
from django.utils import timezone
import requests
import logging

from .models import (
    CourseCategory, Course, Lesson, UserProgress, UserNote,
    AIConfig, ChatHistory
)
from .serializers import (
    CourseCategorySerializer, CourseListSerializer, CourseDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    UserProgressSerializer, UserNoteSerializer,
    AIConfigSerializer, ChatHistorySerializer, ChatMessageSerializer
)
from .ai_service import AIServiceFactory


logger = logging.getLogger(__name__)


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


class AIConfigViewSet(viewsets.ModelViewSet):
    """AI配置视图集"""
    serializer_class = AIConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConfig.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            config, created = AIConfig.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data
            )

        response_serializer = self.get_serializer(config)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status_code, headers=headers)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前用户的激活配置"""
        config = AIConfig.objects.filter(user=request.user, is_active=True).first()
        if config:
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        return Response({'detail': '未配置AI服务'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def models(self, request):
        """获取可用模型列表"""
        provider = request.query_params.get('provider')
        api_endpoint = request.query_params.get('api_endpoint')

        # 当查询参数缺失时尝试使用当前配置
        if not provider or not api_endpoint:
            current_config = AIConfig.objects.filter(user=request.user).first()
            if current_config:
                provider = provider or current_config.provider
                api_endpoint = api_endpoint or current_config.api_endpoint

        if not provider:
            return Response({'detail': '缺少provider参数'}, status=status.HTTP_400_BAD_REQUEST)

        if provider not in ('ollama_local', 'ollama_remote'):
            return Response({'detail': '当前仅支持同步Ollama模型'}, status=status.HTTP_400_BAD_REQUEST)

        if not api_endpoint:
            return Response({'detail': '缺少api_endpoint参数'}, status=status.HTTP_400_BAD_REQUEST)

        endpoint = api_endpoint.rstrip('/')

        try:
            resp = requests.get(f'{endpoint}/api/tags', timeout=10)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            logger.warning('无法连接到 Ollama 服务: %s', exc)
            fallback_models = [
                {'name': 'qwen3:8b', 'display_name': 'qwen3:8b'},
                {'name': 'llama3:8b', 'display_name': 'llama3:8b'},
            ]
            return Response(
                {
                    'models': fallback_models,
                    'warning': '无法连接到 Ollama 服务，请检查服务是否已启动或更新端点配置。已提供默认模型列表以便继续配置。'
                }
            )

        data = resp.json() if resp.content else {}
        models = data.get('models') or data.get('data') or []

        normalized = []
        for item in models:
            if isinstance(item, str):
                normalized.append({'name': item, 'display_name': item})
                continue

            name = item.get('name') or item.get('model') or item.get('id')
            if not name:
                continue

            normalized.append({
                'name': name,
                'display_name': item.get('display_name') or name,
                'size': item.get('size') or item.get('size_blobs') or item.get('details', {}).get('parameter_size')
            })

        return Response({'models': normalized})
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试AI配置"""
        config = self.get_object()
        
        try:
            ai_service = AIServiceFactory.create(config)
            messages = [{'role': 'user', 'content': 'Hello'}]
            response = ai_service.chat(messages)
            return Response({'status': 'success', 'response': response})
        except Exception as e:
            return Response(
                {'status': 'error', 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatViewSet(viewsets.ViewSet):
    """AI对话视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """发送消息"""
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())
        extra_context = serializer.validated_data.get('extra_context', {})
        
        # 获取用户的AI配置
        ai_config = AIConfig.objects.filter(user=request.user, is_active=True).first()
        if not ai_config:
            return Response(
                {'error': '请先配置AI服务'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 保存用户消息
        ChatHistory.objects.create(
            user=request.user,
            session_id=session_id,
            role='user',
            content=message,
            context=extra_context
        )
        
        try:
            # 获取历史对话
            history = ChatHistory.objects.filter(
                user=request.user,
                session_id=session_id
            ).order_by('created_at')[:20]  # 最近20条
            
            # 构建消息列表
            messages = []
            for msg in history:
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # 调用AI服务
            ai_service = AIServiceFactory.create(ai_config)
            response_content = ai_service.chat(messages)
            
            # 保存AI响应
            assistant_msg = ChatHistory.objects.create(
                user=request.user,
                session_id=session_id,
                role='assistant',
                content=response_content
            )
            
            return Response({
                'session_id': session_id,
                'message': response_content,
                'timestamp': assistant_msg.created_at
            })
        
        except Exception as e:
            return Response(
                {'error': f'AI服务调用失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取聊天历史"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': '缺少session_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = ChatHistory.objects.filter(
            user=request.user,
            session_id=session_id
        ).order_by('created_at')
        
        serializer = ChatHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """获取用户的所有会话列表"""
        # 获取所有不同的session_id及其最新消息
        sessions = ChatHistory.objects.filter(
            user=request.user
        ).values('session_id').distinct()
        
        session_list = []
        for session in sessions:
            sid = session['session_id']
            last_msg = ChatHistory.objects.filter(
                user=request.user,
                session_id=sid
            ).order_by('-created_at').first()
            
            if last_msg:
                session_list.append({
                    'session_id': sid,
                    'last_message': last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content,
                    'updated_at': last_msg.created_at
                })
        
        # 按时间倒序
        session_list.sort(key=lambda x: x['updated_at'], reverse=True)
        return Response(session_list)
