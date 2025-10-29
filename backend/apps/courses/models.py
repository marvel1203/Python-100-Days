from django.db import models
from django.contrib.auth.models import User


class CourseCategory(models.Model):
    """课程分类"""
    name = models.CharField('分类名称', max_length=50)
    slug = models.SlugField('URL标识', max_length=50, unique=True)
    description = models.TextField('分类描述', blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '课程分类'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """课程"""
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='所属分类'
    )
    title = models.CharField('课程标题', max_length=200)
    slug = models.SlugField('URL标识', max_length=200, unique=True)
    description = models.TextField('课程描述')
    day_range = models.CharField('天数范围', max_length=20, help_text='例如: Day01-20')
    cover_image = models.ImageField('封面图', upload_to='courses/covers/', blank=True)
    difficulty = models.CharField(
        '难度级别',
        max_length=20,
        choices=[
            ('beginner', '入门'),
            ('intermediate', '进阶'),
            ('advanced', '高级'),
        ],
        default='beginner'
    )
    order = models.IntegerField('排序', default=0)
    is_published = models.BooleanField('是否发布', default=True)
    view_count = models.IntegerField('浏览次数', default=0)
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.day_range} - {self.title}"


class Lesson(models.Model):
    """每日课程"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='所属课程'
    )
    day_number = models.IntegerField('天数')
    title = models.CharField('课程标题', max_length=200)
    slug = models.SlugField('URL标识', max_length=200)
    content = models.TextField('课程内容(Markdown)')
    summary = models.TextField('课程摘要', blank=True)
    code_url = models.URLField('代码链接', blank=True, help_text='GitHub代码链接')
    video_url = models.URLField('视频链接', blank=True)
    estimated_time = models.IntegerField('预计学习时长(分钟)', default=60)
    order = models.IntegerField('排序', default=0)
    is_published = models.BooleanField('是否发布', default=True)
    view_count = models.IntegerField('浏览次数', default=0)
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '课程课时'
        verbose_name_plural = verbose_name
        ordering = ['course', 'day_number']
        unique_together = ['course', 'day_number']
    
    def __str__(self):
        return f"Day{self.day_number:02d} - {self.title}"


class LessonResource(models.Model):
    """课程资源"""
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='所属课时'
    )
    title = models.CharField('资源标题', max_length=200)
    file = models.FileField('资源文件', upload_to='lessons/resources/')
    file_type = models.CharField(
        '文件类型',
        max_length=20,
        choices=[
            ('code', '代码文件'),
            ('pdf', 'PDF文档'),
            ('image', '图片'),
            ('other', '其他'),
        ]
    )
    file_size = models.IntegerField('文件大小(字节)', default=0)
    download_count = models.IntegerField('下载次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lesson} - {self.title}"


class UserProgress(models.Model):
    """用户学习进度"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_progress',
        verbose_name='用户'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='课时'
    )
    status = models.CharField(
        '学习状态',
        max_length=20,
        choices=[
            ('not_started', '未开始'),
            ('in_progress', '学习中'),
            ('completed', '已完成'),
        ],
        default='not_started'
    )
    progress_percentage = models.IntegerField('完成百分比', default=0)
    study_time = models.IntegerField('学习时长(分钟)', default=0)
    started_at = models.DateTimeField('开始学习时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    last_accessed = models.DateTimeField('最后访问时间', auto_now=True)
    
    class Meta:
        verbose_name = '学习进度'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'lesson']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson}"


class UserNote(models.Model):
    """用户笔记"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='用户'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='课时'
    )
    content = models.TextField('笔记内容')
    is_public = models.BooleanField('是否公开', default=False)
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '学习笔记'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的笔记 - {self.lesson}"


class AIConfig(models.Model):
    """AI配置"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ai_config',
        verbose_name='用户'
    )
    provider = models.CharField(
        'AI服务提供商',
        max_length=50,
        choices=[
            ('ollama_local', 'Ollama本地'),
            ('ollama_remote', 'Ollama远程'),
            ('deepseek', 'DeepSeek'),
            ('openai', 'OpenAI'),
        ],
        default='ollama_local'
    )
    api_endpoint = models.URLField('API端点', default='http://localhost:11434')
    api_key = models.CharField('API密钥', max_length=255, blank=True)
    model_name = models.CharField('模型名称', max_length=100, default='llama2')
    temperature = models.FloatField('温度参数', default=0.7)
    max_tokens = models.IntegerField('最大tokens', default=2000)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'AI配置'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username}的AI配置 - {self.provider}"


class ChatHistory(models.Model):
    """聊天历史"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_history',
        verbose_name='用户'
    )
    session_id = models.CharField('会话ID', max_length=100, db_index=True)
    role = models.CharField(
        '角色',
        max_length=20,
        choices=[
            ('user', '用户'),
            ('assistant', '助手'),
            ('system', '系统'),
        ]
    )
    content = models.TextField('消息内容')
    context = models.JSONField('上下文信息', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '聊天历史'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'session_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.created_at}"
