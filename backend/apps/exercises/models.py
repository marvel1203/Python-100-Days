from django.db import models
from django.contrib.auth.models import User
from apps.courses.models import Lesson


class Exercise(models.Model):
    """编程练习"""
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name='所属课时',
        null=True,
        blank=True
    )
    title = models.CharField('练习标题', max_length=200)
    slug = models.SlugField('URL标识', max_length=200, unique=True)
    difficulty = models.CharField(
        '难度级别',
        max_length=20,
        choices=[
            ('easy', '简单'),
            ('medium', '中等'),
            ('hard', '困难'),
        ],
        default='easy'
    )
    problem_description = models.TextField('问题描述')
    input_format = models.TextField('输入格式说明', blank=True)
    output_format = models.TextField('输出格式说明', blank=True)
    constraints = models.TextField('约束条件', blank=True)
    examples = models.JSONField('示例', default=list, help_text='[{"input": "...", "output": "...", "explanation": "..."}]')
    test_cases = models.JSONField('测试用例', default=list, help_text='[{"input": "...", "output": "..."}]')
    template_code = models.TextField('代码模板', blank=True)
    solution = models.TextField('参考解答', blank=True)
    tags = models.CharField('标签', max_length=200, blank=True, help_text='用逗号分隔')
    acceptance_rate = models.FloatField('通过率', default=0.0)
    submit_count = models.IntegerField('提交次数', default=0)
    accepted_count = models.IntegerField('通过次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '编程练习'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Submission(models.Model):
    """代码提交记录"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='用户'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='练习'
    )
    code = models.TextField('提交代码')
    language = models.CharField(
        '编程语言',
        max_length=20,
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('java', 'Java'),
        ],
        default='python'
    )
    status = models.CharField(
        '运行状态',
        max_length=30,
        choices=[
            ('pending', '等待中'),
            ('running', '运行中'),
            ('accepted', '通过'),
            ('wrong_answer', '答案错误'),
            ('runtime_error', '运行错误'),
            ('time_limit_exceeded', '超时'),
            ('memory_limit_exceeded', '内存超限'),
        ],
        default='pending'
    )
    result = models.JSONField('运行结果', default=dict, blank=True)
    execution_time = models.IntegerField('执行时间(ms)', default=0)
    memory_used = models.IntegerField('内存使用(KB)', default=0)
    created_at = models.DateTimeField('提交时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '代码提交'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} - {self.status}"
