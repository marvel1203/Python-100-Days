from rest_framework import serializers
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
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'day_range', 'cover_image',
            'difficulty', 'category', 'lessons', 'view_count', 'like_count',
            'created_at', 'updated_at'
        ]


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
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'day_number', 'title', 'slug', 'content', 'summary',
            'code_url', 'video_url', 'estimated_time', 'course_title', 'course_slug',
            'resources', 'user_progress', 'view_count', 'like_count',
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

