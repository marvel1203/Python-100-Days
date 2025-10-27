"""
练习题导入脚本
从课程内容中提取代码示例作为练习题
"""
import re
from django.core.management.base import BaseCommand
from apps.courses.models import Lesson
from apps.exercises.models import Exercise


class Command(BaseCommand):
    help = '从课程内容中提取练习题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有练习题后再导入',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('清空现有练习题...'))
            Exercise.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('数据已清空'))

        total_exercises = 0

        # 遍历所有课时
        lessons = Lesson.objects.all()
        
        for lesson in lessons:
            exercises_created = self._extract_exercises_from_lesson(lesson)
            total_exercises += exercises_created
            
            if exercises_created > 0:
                self.stdout.write(
                    f'  课时 "{lesson.title}": 创建 {exercises_created} 个练习'
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n导入完成! 共创建 {total_exercises} 个练习题'
        ))

    def _extract_exercises_from_lesson(self, lesson):
        """从课时内容中提取练习题"""
        content = lesson.content
        exercises_created = 0

        # 提取代码块
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        # 提取例子标题和代码
        examples = re.findall(
            r'####\s*例子\d+[：:](.*?)\n.*?```python\n(.*?)\n```',
            content,
            re.DOTALL
        )

        for idx, (title, code) in enumerate(examples, start=1):
            title = title.strip()
            code = code.strip()
            
            # 跳过太短的代码
            if len(code) < 50:
                continue
            
            # 从代码注释中提取描述
            description_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
            if description_match:
                description = description_match.group(1).strip()
            else:
                description = f"完成示例: {title}"
            
            # 提取初始代码(去掉注释后的代码,作为模板)
            initial_code = self._generate_initial_code(code)
            
            # 创建练习题
            from django.utils.text import slugify
            exercise, created = Exercise.objects.get_or_create(
                lesson=lesson,
                title=title,
                defaults={
                    'slug': slugify(f"{lesson.id}-{title}-{idx}"),
                    'problem_description': description,
                    'difficulty': self._determine_difficulty(lesson.day_number),
                    'template_code': initial_code,
                    'solution': code,
                    'test_cases': self._generate_test_cases_json(title),
                    'examples': self._generate_examples_json(title),
                }
            )
            
            if created:
                exercises_created += 1

        return exercises_created

    def _generate_initial_code(self, solution_code):
        """生成初始代码模板"""
        lines = solution_code.split('\n')
        
        # 保留注释和函数定义,其他内容用注释提示
        initial_lines = []
        in_docstring = False
        
        for line in lines:
            if '"""' in line:
                in_docstring = not in_docstring
                initial_lines.append(line)
            elif in_docstring or line.strip().startswith('#') or not line.strip():
                initial_lines.append(line)
            elif line.strip().startswith('def ') or line.strip().startswith('class '):
                initial_lines.append(line)
                initial_lines.append('    # 在这里编写你的代码')
            elif 'input(' in line:
                initial_lines.append(line)
        
        if not initial_lines:
            return '# 在这里编写你的代码\n'
        
        return '\n'.join(initial_lines)

    def _determine_difficulty(self, day_number):
        """根据天数确定难度"""
        if day_number <= 10:
            return 'easy'
        elif day_number <= 50:
            return 'medium'
        else:
            return 'hard'

    def _generate_test_cases_json(self, title):
        """生成测试用例(JSON格式)"""
        return [
            {
                "input": "请根据题目要求输入",
                "output": "期望输出"
            }
        ]
    
    def _generate_examples_json(self, title):
        """生成示例(JSON格式)"""
        return [
            {
                "input": "示例输入",
                "output": "示例输出",
                "explanation": "这是一个示例"
            }
        ]

    def _generate_test_cases(self, title):
        """生成测试用例(示例) - 已弃用"""
        # 这里返回一个简单的JSON字符串示例
        # 实际项目中应该根据题目类型生成真实的测试用例
        return '''[
    {
        "input": "请根据题目要求输入",
        "expected_output": "期望输出",
        "description": "测试用例1"
    }
]'''
