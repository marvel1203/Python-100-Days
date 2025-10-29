from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseCategoryViewSet, CourseViewSet, LessonViewSet,
    UserProgressViewSet, UserNoteViewSet,
    AIConfigViewSet, ChatViewSet
)

router = DefaultRouter()
router.register('categories', CourseCategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('progress', UserProgressViewSet, basename='progress')
router.register('notes', UserNoteViewSet, basename='note')
router.register('ai-config', AIConfigViewSet, basename='ai-config')
router.register('chat', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
