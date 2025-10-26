from django.contrib import admin
from .models import CourseCategory, Course, Lesson, LessonResource, UserProgress, UserNote


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'day_range', 'difficulty', 'is_published', 'view_count', 'like_count']
    list_filter = ['category', 'difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'like_count', 'created_at', 'updated_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'day_number', 'is_published', 'view_count', 'like_count']
    list_filter = ['course', 'is_published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'like_count', 'created_at', 'updated_at']


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'file_type', 'file_size', 'download_count']
    list_filter = ['file_type']
    search_fields = ['title']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'progress_percentage', 'completed_at']
    list_filter = ['status']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['last_accessed']


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_public', 'like_count', 'created_at']
    list_filter = ['is_public']
    search_fields = ['user__username', 'content']
