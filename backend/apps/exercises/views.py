from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from .models import Exercise, Submission
from .serializers import ExerciseListSerializer, ExerciseDetailSerializer, SubmissionSerializer
from .code_executor import CodeExecutor


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
        
        if not code:
            return Response({
                'success': False,
                'error': '代码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 验证代码安全性
            executor = CodeExecutor()
            is_valid, error_msg = executor.validate_code(code)
            if not is_valid:
                return Response({
                    'success': False,
                    'error': f'代码安全验证失败: {error_msg}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 执行代码
            result = executor.execute(code)
            
            return Response({
                'success': result['status'] != 'error',
                'output': result['output'],
                'error': result.get('error_message'),
                'execution_time': result['execution_time']
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, slug=None):
        """提交练习题答案"""
        exercise = self.get_object()
        code = request.data.get('code', '')
        language = request.data.get('language', 'python')
        
        if not code:
            return Response(
                {'error': '代码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证代码安全性
        executor = CodeExecutor()
        is_valid, error_msg = executor.validate_code(code)
        if not is_valid:
            return Response(
                {'error': f'代码安全验证失败: {error_msg}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建提交记录
        submission = Submission.objects.create(
            exercise=exercise,
            user=request.user,
            code=code,
            language=language,
            status='running'
        )
        
        try:
            # 执行代码并运行测试用例
            result = executor.execute(code, exercise.test_cases)
            
            # 更新提交记录
            if result['status'] == 'passed':
                submission.status = 'accepted'
            elif result['status'] == 'failed':
                submission.status = 'wrong_answer'
            else:
                submission.status = 'runtime_error'
            
            submission.result = {
                'output': result['output'],
                'error': result.get('error_message'),
                'test_results': result.get('test_results', [])
            }
            submission.execution_time = int(result['execution_time'] * 1000)  # 转为毫秒
            submission.memory_used = result.get('memory_usage', 0)
            submission.save()
            
            # 更新练习题统计
            Exercise.objects.filter(pk=exercise.pk).update(
                submit_count=F('submit_count') + 1,
                accepted_count=F('accepted_count') + (1 if submission.status == 'accepted' else 0)
            )
            
            # 更新acceptance_rate
            exercise.refresh_from_db()
            if exercise.submit_count > 0:
                exercise.acceptance_rate = round(exercise.accepted_count / exercise.submit_count * 100, 2)
                exercise.save()
            
            serializer = SubmissionSerializer(submission)
            return Response(serializer.data)
        
        except Exception as e:
            submission.status = 'runtime_error'
            submission.result = {'error': str(e)}
            submission.save()
            return Response(
                {'error': f'执行失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
