from django.core.management.base import BaseCommand
from apps.courses.models import Lesson


class Command(BaseCommand):
    help = '修复课时的slug,确保唯一性'

    def handle(self, *args, **options):
        lessons = Lesson.objects.all().select_related('course')
        updated_count = 0
        
        for lesson in lessons:
            # 生成唯一的slug: 课程slug-day编号
            # 例如: day0120-01, day0120-02
            new_slug = f"{lesson.course.slug}-day{lesson.day_number:02d}"
            
            if lesson.slug != new_slug:
                self.stdout.write(
                    f'更新 {lesson.id}: {lesson.slug} -> {new_slug}'
                )
                lesson.slug = new_slug
                lesson.save(update_fields=['slug'])
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n完成! 共更新 {updated_count} 个课时的slug')
        )
