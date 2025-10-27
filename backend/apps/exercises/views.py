from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import subprocess
import tempfile
import os
import time
import sys

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
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def run_code(self, request):
        """运行Python代码（允许匿名访问）"""
        code = request.data.get('code', '')
        stdin_data = request.data.get('stdin', '')
        
        if not code:
            return Response({
                'success': False,
                'error': '代码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 使用Docker运行Python代码
            result = self._execute_python_code(code, stdin_data)
            return Response(result)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _execute_python_code(self, code, stdin_data=''):
        """执行Python代码（临时方案：直接执行，生产环境需要添加Docker沙箱）"""
        try:
            start_time = time.time()
            
            # 使用subprocess在当前环境执行
            # 注意：这是MVP方案，生产环境应使用Docker沙箱隔离
            result = subprocess.run(
                [sys.executable, '-c', code],
                input=stdin_data.encode() if stdin_data else None,
                capture_output=True,
                timeout=5,  # 5秒超时
                env={'PYTHONPATH': ''}  # 清空PYTHONPATH避免意外导入
            )
            
            execution_time = time.time() - start_time
            
            # 获取输出
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': stdout,
                    'error': None,
                    'execution_time': round(execution_time, 3)
                }
            else:
                return {
                    'success': False,
                    'output': stdout,
                    'error': stderr,
                    'execution_time': round(execution_time, 3)
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '代码执行超时（超过5秒）',
                'output': '',
                'execution_time': 5.0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行错误: {str(e)}',
                'output': '',
                'execution_time': 0
            }


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
