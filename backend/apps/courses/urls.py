from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseCategoryViewSet, CourseViewSet, LessonViewSet,
    UserProgressViewSet, UserNoteViewSet
)

router = DefaultRouter()
router.register('categories', CourseCategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('progress', UserProgressViewSet, basename='progress')
router.register('notes', UserNoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
