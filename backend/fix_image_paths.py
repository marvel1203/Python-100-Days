#!/usr/bin/env python
"""修复课时内容中的图片路径"""
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.courses.models import Lesson, Course

def fix_image_paths(content, course_dir):
    """将错误的路径转换为正确的路径"""
    # 替换 /course-res/course_resources/ 为 /course-res/{course_dir}/
    content = re.sub(
        r'/course-res/course_resources/',
        f'/course-res/{course_dir}/',
        content
    )
    return content

# 课程 slug 到文件夹名的映射
course_folders = {
    'day0120': 'Day01-20',
    'day2130': 'Day21-30',
    'day3135': 'Day31-35',
    'day3645': 'Day36-45',
    'day4660': 'Day46-60',
    'day6165': 'Day61-65',
    'day6680': 'Day66-80',
    'day8190': 'Day81-90',
    'day91100': 'Day91-100',
}

updated = 0
for course_slug, folder_name in course_folders.items():
    course = Course.objects.filter(slug=course_slug).first()
    if course:
        lessons = course.lessons.all()
        print(f'处理课程: {course.title} ({len(lessons)} 个课时)')
        for lesson in lessons:
            # 检查是否需要修复（查找错误的路径）
            if '/course-res/course_resources/' in lesson.content:
                new_content = fix_image_paths(lesson.content, folder_name)
                lesson.content = new_content
                lesson.save()
                updated += 1
                print(f'  - 已更新: {lesson.title}')

print(f'\n总计更新 {updated} 个课时的图片路径')
