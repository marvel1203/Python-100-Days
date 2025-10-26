from rest_framework import serializers
from .models import Exercise, Submission


class ExerciseListSerializer(serializers.ModelSerializer):
    """练习列表序列化器"""
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'difficulty', 'tags_list',
            'acceptance_rate', 'submit_count', 'accepted_count'
        ]
    
    def get_tags_list(self, obj):
        return obj.tags.split(',') if obj.tags else []


class ExerciseDetailSerializer(serializers.ModelSerializer):
    """练习详情序列化器"""
    tags_list = serializers.SerializerMethodField()
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'difficulty', 'problem_description',
            'input_format', 'output_format', 'constraints', 'examples',
            'template_code', 'tags_list', 'lesson_title',
            'acceptance_rate', 'submit_count', 'accepted_count', 'created_at'
        ]
    
    def get_tags_list(self, obj):
        return obj.tags.split(',') if obj.tags else []


class SubmissionSerializer(serializers.ModelSerializer):
    """代码提交序列化器"""
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'exercise', 'exercise_title', 'code', 'language',
            'status', 'result', 'execution_time', 'memory_used', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'result', 'execution_time', 'memory_used']
