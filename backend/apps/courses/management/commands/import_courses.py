"""
课程内容导入脚本
从 Day01-100 的 Markdown 文件导入课程数据
"""
import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.courses.models import CourseCategory, Course, Lesson


class Command(BaseCommand):
    help = '从 Markdown 文件导入课程数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有课程数据后再导入',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('清空现有课程数据...'))
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            CourseCategory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('数据已清空'))

        # 项目根目录 - 在容器中Day文件夹被复制到了/data目录
        base_dir = Path('/data')

        # 定义课程分类
        categories_data = [
            {
                'name': 'Python基础',
                'description': 'Python语言基础知识,包括语法、数据结构、函数、面向对象等',
                'folders': ['Day01-20'],
                'order': 1
            },
            {
                'name': 'Python进阶',
                'description': 'Python进阶内容,包括文件操作、网络编程、数据库等',
                'folders': ['Day21-30', 'Day31-35', 'Day36-45'],
                'order': 2
            },
            {
                'name': 'Web开发',
                'description': 'Django/Flask Web开发框架及项目实战',
                'folders': ['Day46-60'],
                'order': 3
            },
            {
                'name': '数据采集',
                'description': '网络爬虫技术及数据采集实战',
                'folders': ['Day61-65'],
                'order': 4
            },
            {
                'name': '数据分析',
                'description': '数据分析与可视化,包括NumPy、Pandas等',
                'folders': ['Day66-80'],
                'order': 5
            },
            {
                'name': '项目实战',
                'description': '综合项目实战案例',
                'folders': ['Day81-90', 'Day91-100'],
                'order': 6
            },
        ]

        total_courses = 0
        total_lessons = 0

        for cat_data in categories_data:
            self.stdout.write(f"\n处理分类: {cat_data['name']}")
            
            # 创建分类
            category, created = CourseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'slug': f"category-{cat_data['order']}",
                    'order': cat_data['order']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  创建分类: {category.name}'))

            # 处理每个文件夹
            for folder in cat_data['folders']:
                folder_path = base_dir / folder
                if not folder_path.exists():
                    self.stdout.write(self.style.WARNING(f'  文件夹不存在: {folder}'))
                    continue

                # 创建课程(每个文件夹一个课程)
                course_name = self._get_course_name(folder)
                course_slug = folder.lower().replace('-', '')  # Day01-20 -> day0120
                course, created = Course.objects.get_or_create(
                    title=course_name,
                    category=category,
                    defaults={
                        'description': self._get_course_description(folder),
                        'slug': course_slug,
                        'difficulty': self._get_course_level(folder),
                        'day_range': folder,
                        'order': self._extract_day_number(folder)
                    }
                )
                
                if created:
                    total_courses += 1
                    self.stdout.write(self.style.SUCCESS(f'  创建课程: {course.title}'))

                # 导入课程的所有课时(Markdown文件)
                md_files = sorted(folder_path.glob('*.md'))
                for idx, md_file in enumerate(md_files, start=1):
                    lesson_data = self._parse_markdown_file(md_file)
                    
                    from django.utils.text import slugify
                    lesson, created = Lesson.objects.get_or_create(
                        course=course,
                        day_number=idx,
                        defaults={
                            'title': lesson_data['title'],
                            'slug': slugify(lesson_data['title']) + f'-{idx}',
                            'content': lesson_data['content'],
                            'order': idx,
                            'estimated_time': self._estimate_duration(lesson_data['content'])
                        }
                    )
                    
                    if created:
                        total_lessons += 1
                        self.stdout.write(f'    - 课时 {idx}: {lesson.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\n导入完成! 共创建 {total_courses} 个课程, {total_lessons} 个课时'
        ))

    def _get_course_name(self, folder):
        """根据文件夹名生成课程名称"""
        mapping = {
            'Day01-20': 'Python基础(Day01-20)',
            'Day21-30': 'Python进阶-文件与数据处理',
            'Day31-35': 'Python进阶-Web前端与Linux',
            'Day36-45': 'Python进阶-数据库',
            'Day46-60': 'Django Web开发',
            'Day61-65': 'Python网络爬虫',
            'Day66-80': 'Python数据分析',
            'Day81-90': 'Python项目实战(一)',
            'Day91-100': 'Python项目实战(二)',
        }
        return mapping.get(folder, folder)

    def _get_course_description(self, folder):
        """根据文件夹名生成课程描述"""
        mapping = {
            'Day01-20': '从零开始学习Python语言基础,包括变量、运算符、控制结构、数据结构、函数和面向对象编程',
            'Day21-30': '学习Python文件操作、异常处理、CSV/Excel/Word/PDF处理、图像处理等进阶内容',
            'Day31-35': '深入学习Python语言特性,了解Web前端基础和Linux操作系统',
            'Day36-45': '学习关系型数据库MySQL的使用,掌握SQL语言和Python操作数据库',
            'Day46-60': '使用Django框架开发Web应用,学习模型、视图、模板、DRF等核心内容',
            'Day61-65': '学习网络数据采集技术,掌握requests、BeautifulSoup、Selenium、Scrapy等工具',
            'Day66-80': '学习NumPy、Pandas等数据分析工具,掌握数据处理和可视化技能',
            'Day81-90': '通过实战项目巩固所学知识,提升综合开发能力',
            'Day91-100': '更多实战项目,培养解决实际问题的能力',
        }
        return mapping.get(folder, f'{folder}课程内容')

    def _get_course_level(self, folder):
        """根据文件夹名判断课程难度"""
        if folder.startswith('Day01-20') or folder.startswith('Day21-30'):
            return 'beginner'
        elif folder.startswith('Day31') or folder.startswith('Day36') or folder.startswith('Day46'):
            return 'intermediate'
        else:
            return 'advanced'

    def _extract_day_number(self, folder):
        """从文件夹名提取起始天数作为排序依据"""
        match = re.search(r'Day(\d+)', folder)
        return int(match.group(1)) if match else 0

    def _parse_markdown_file(self, md_file):
        """解析Markdown文件,提取标题和内容"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题(去掉文件名中的编号)
            filename = md_file.stem
            # 匹配模式: "01.初识Python" -> "初识Python"
            title_match = re.match(r'^\d+\.(.+)$', filename)
            if title_match:
                title = title_match.group(1)
            else:
                title = filename
            
            return {
                'title': title,
                'content': content
            }
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'读取文件失败 {md_file}: {e}'))
            return {
                'title': md_file.stem,
                'content': ''
            }

    def _estimate_duration(self, content):
        """根据内容长度估算课时时长(分钟)"""
        # 简单估算: 每500字约5分钟
        char_count = len(content)
        duration = max(5, min(120, char_count // 100))  # 5-120分钟
        return duration
