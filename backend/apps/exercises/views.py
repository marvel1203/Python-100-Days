from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import docker
import tempfile
import os
import time

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
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def run_code(self, request):
        """运行Python代码"""
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
        """在Docker容器中安全执行Python代码"""
        try:
            # 创建临时文件保存代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # 创建Docker客户端
            client = docker.from_env()
            
            # 读取代码文件内容
            with open(temp_file, 'r') as f:
                code_content = f.read()
            
            # 运行Docker容器
            container = client.containers.run(
                'python:3.11-slim',
                command=['python', '-c', code_content],
                stdin_open=True,
                stdout=True,
                stderr=True,
                detach=True,
                mem_limit='128m',  # 限制内存
                cpu_period=100000,
                cpu_quota=50000,   # 限制CPU使用率50%
                network_disabled=True,  # 禁用网络
                remove=True  # 运行完自动删除
            )
            
            # 如果有输入数据，发送到容器
            if stdin_data:
                container.put_archive('/', stdin_data.encode())
            
            # 等待容器完成（最多5秒）
            start_time = time.time()
            timeout = 5
            
            while container.status != 'exited':
                if time.time() - start_time > timeout:
                    container.stop(timeout=1)
                    container.kill()
                    return {
                        'success': False,
                        'error': '代码执行超时（超过5秒）',
                        'output': '',
                        'execution_time': timeout
                    }
                time.sleep(0.1)
                container.reload()
            
            # 获取输出
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            execution_time = time.time() - start_time
            
            # 获取退出码
            exit_code = container.wait()['StatusCode']
            
            # 清理临时文件
            os.unlink(temp_file)
            
            return {
                'success': exit_code == 0,
                'output': logs,
                'error': logs if exit_code != 0 else None,
                'execution_time': round(execution_time, 3)
            }
            
        except docker.errors.ContainerError as e:
            return {
                'success': False,
                'error': f'容器错误: {str(e)}',
                'output': str(e),
                'execution_time': 0
            }
        except docker.errors.ImageNotFound:
            return {
                'success': False,
                'error': 'Python镜像未找到，请联系管理员',
                'output': '',
                'execution_time': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'执行错误: {str(e)}',
                'output': '',
                'execution_time': 0
            }
        finally:
            # 确保临时文件被删除
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.unlink(temp_file)


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
