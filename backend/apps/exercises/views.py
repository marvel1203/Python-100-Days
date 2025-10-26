from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Exercise, Submission
from .serializers import ExerciseListSerializer, ExerciseDetailSerializer, SubmissionSerializer


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """练习视图集"""
    queryset = Exercise.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'lesson']
    search_fields = ['title', 'problem_description', 'tags']
    ordering_fields = ['created_at', 'difficulty', 'acceptance_rate']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExerciseDetailSerializer
        return ExerciseListSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    """代码提交视图集"""
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exercise', 'status', 'language']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related('exercise')
    
    def perform_create(self, serializer):
        submission = serializer.save(user=self.request.user)
        # TODO: 异步执行代码 - 使用Celery任务
        # from .tasks import execute_code
        # execute_code.delay(submission.id)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取提交统计"""
        queryset = self.get_queryset()
        total = queryset.count()
        accepted = queryset.filter(status='accepted').count()
        
        return Response({
            'total_submissions': total,
            'accepted': accepted,
            'acceptance_rate': round(accepted / total * 100, 2) if total > 0 else 0
        })
