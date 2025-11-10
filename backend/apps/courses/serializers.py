from rest_framework import serializers
from django.db.models import Q
from .models import (
    CourseCategory, Course, Lesson, LessonResource, UserProgress, UserNote,
    AIConfig, ChatHistory
)


class CourseCategorySerializer(serializers.ModelSerializer):
    """课程分类序列化器"""
    courses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'slug', 'description', 'order', 'courses_count', 'created_at']
    
    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()


class LessonListSerializer(serializers.ModelSerializer):
    """课程列表序列化器(简化版)"""
    class Meta:
        model = Lesson
        fields = ['id', 'day_number', 'title', 'slug', 'summary', 'estimated_time', 'view_count', 'like_count']


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'day_range', 'cover_image',
            'difficulty', 'category_name', 'lessons_count', 'view_count', 'like_count',
            'created_at', 'updated_at'
        ]
    
    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_published=True).count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器"""
    category = CourseCategorySerializer(read_only=True)
    lessons = LessonListSerializer(many=True, read_only=True)
    previous_course = serializers.SerializerMethodField()
    next_course = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'day_range', 'cover_image',
            'difficulty', 'category', 'lessons', 'view_count', 'like_count',
            'previous_course', 'next_course',
            'created_at', 'updated_at'
        ]

    def _build_navigation_payload(self, course):
        if not course:
            return None
        return {
            'slug': course.slug,
            'title': course.title,
            'day_range': course.day_range,
        }

    def get_previous_course(self, obj):
        queryset = Course.objects.filter(is_published=True).exclude(pk=obj.pk)
        queryset = queryset.filter(
            Q(order__lt=obj.order) |
            (Q(order=obj.order) & Q(id__lt=obj.id))
        ).order_by('-order', '-id')
        previous_course = queryset.first()
        return self._build_navigation_payload(previous_course)

    def get_next_course(self, obj):
        queryset = Course.objects.filter(is_published=True).exclude(pk=obj.pk)
        queryset = queryset.filter(
            Q(order__gt=obj.order) |
            (Q(order=obj.order) & Q(id__gt=obj.id))
        ).order_by('order', 'id')
        next_course = queryset.first()
        return self._build_navigation_payload(next_course)


class LessonResourceSerializer(serializers.ModelSerializer):
    """课程资源序列化器"""
    class Meta:
        model = LessonResource
        fields = ['id', 'title', 'file', 'file_type', 'file_size', 'download_count', 'created_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    resources = LessonResourceSerializer(many=True, read_only=True)
    user_progress = serializers.SerializerMethodField()
    previous_lesson = serializers.SerializerMethodField()
    next_lesson = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'day_number', 'title', 'slug', 'content', 'summary',
            'code_url', 'video_url', 'estimated_time', 'course_title', 'course_slug',
            'resources', 'user_progress', 'previous_lesson', 'next_lesson',
            'view_count', 'like_count',
            'created_at', 'updated_at'
        ]
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, lesson=obj)
                return {
                    'status': progress.status,
                    'progress_percentage': progress.progress_percentage,
                    'study_time': progress.study_time
                }
            except UserProgress.DoesNotExist:
                return None
        return None

    def _build_navigation_payload(self, lesson):
        if not lesson:
            return None
        course = getattr(lesson, 'course', None)
        return {
            'slug': lesson.slug,
            'title': lesson.title,
            'day_number': lesson.day_number,
            'course_slug': getattr(course, 'slug', None),
            'course_title': getattr(course, 'title', None),
        }

    def get_previous_lesson(self, obj):
        # 优先查找同一课程内的上一课时，若不存在则尝试跨课程回溯
        internal_queryset = Lesson.objects.filter(
            course=obj.course,
            is_published=True
        ).exclude(pk=obj.pk)
        internal_queryset = internal_queryset.filter(
            Q(order__lt=obj.order) |
            (Q(order=obj.order) & Q(day_number__lt=obj.day_number)) |
            (Q(order=obj.order) & Q(day_number=obj.day_number) & Q(id__lt=obj.id))
        ).order_by('-order', '-day_number', '-id')

        candidate = internal_queryset.first()
        if candidate:
            return self._build_navigation_payload(candidate)

        cross_queryset = Lesson.objects.filter(is_published=True).exclude(pk=obj.pk)
        cross_queryset = cross_queryset.filter(
            Q(course__order__lt=obj.course.order) |
            (Q(course__order=obj.course.order) & Q(order__lt=obj.order)) |
            (Q(course__order=obj.course.order) & Q(order=obj.order) & Q(day_number__lt=obj.day_number)) |
            (Q(course__order=obj.course.order) & Q(order=obj.order) & Q(day_number=obj.day_number) & Q(id__lt=obj.id))
        ).order_by('-course__order', '-order', '-day_number', '-id')

        return self._build_navigation_payload(cross_queryset.first())

    def get_next_lesson(self, obj):
        # 优先查找同一课程内的下一课时，若不存在则尝试跨课程前进
        internal_queryset = Lesson.objects.filter(
            course=obj.course,
            is_published=True
        ).exclude(pk=obj.pk)
        internal_queryset = internal_queryset.filter(
            Q(order__gt=obj.order) |
            (Q(order=obj.order) & Q(day_number__gt=obj.day_number)) |
            (Q(order=obj.order) & Q(day_number=obj.day_number) & Q(id__gt=obj.id))
        ).order_by('order', 'day_number', 'id')

        candidate = internal_queryset.first()
        if candidate:
            return self._build_navigation_payload(candidate)

        cross_queryset = Lesson.objects.filter(is_published=True).exclude(pk=obj.pk)
        cross_queryset = cross_queryset.filter(
            Q(course__order__gt=obj.course.order) |
            (Q(course__order=obj.course.order) & Q(order__gt=obj.order)) |
            (Q(course__order=obj.course.order) & Q(order=obj.order) & Q(day_number__gt=obj.day_number)) |
            (Q(course__order=obj.course.order) & Q(order=obj.order) & Q(day_number=obj.day_number) & Q(id__gt=obj.id))
        ).order_by('course__order', 'order', 'day_number', 'id')

        return self._build_navigation_payload(cross_queryset.first())


class UserProgressSerializer(serializers.ModelSerializer):
    """学习进度序列化器"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_slug = serializers.CharField(source='lesson.slug', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'lesson_slug', 'course_title',
            'status', 'progress_percentage', 'study_time',
            'started_at', 'completed_at', 'last_accessed'
        ]
        read_only_fields = ['user']


class UserNoteSerializer(serializers.ModelSerializer):
    """学习笔记序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = UserNote
        fields = [
            'id', 'username', 'lesson', 'lesson_title', 'content',
            'is_public', 'like_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'like_count']


class AIConfigSerializer(serializers.ModelSerializer):
    """AI配置序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AIConfig
        fields = [
            'id', 'username', 'provider', 'api_endpoint', 'api_key',
            'model_name', 'temperature', 'max_tokens', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user']
        extra_kwargs = {
            'api_key': {'write_only': True}
        }


class ChatHistorySerializer(serializers.ModelSerializer):
    """聊天历史序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatHistory
        fields = [
            'id', 'username', 'session_id', 'role', 'content',
            'context', 'created_at'
        ]
        read_only_fields = ['user']


class ChatMessageSerializer(serializers.Serializer):
    """聊天消息序列化器"""
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False, allow_blank=True)
    extra_context = serializers.JSONField(required=False, default=dict)

