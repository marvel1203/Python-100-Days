<template>
  <div class="course-detail" v-loading="loading">
    <el-card v-if="course">
      <template #header>
        <div class="course-header">
          <h1>{{ course.title }}</h1>
          <el-tag>{{ course.day_range }}</el-tag>
          <el-tag type="success" style="margin-left: 10px">
            {{ getDifficultyLabel(course.difficulty) }}
          </el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="16">
          <div class="course-description">
            <h3>课程简介</h3>
            <p>{{ course.description }}</p>
          </div>

          <div class="lessons-list">
            <h3>课程内容</h3>
            <el-timeline>
              <el-timeline-item
                v-for="lesson in course.lessons"
                :key="lesson.id"
                placement="top"
              >
                <el-card class="lesson-item" @click="goToLesson(lesson)">
                  <h4>{{ lesson.title }}</h4>
                  <p>{{ lesson.summary }}</p>
                  <div class="lesson-meta">
                    <span><el-icon><Clock /></el-icon> {{ lesson.estimated_time }}分钟</span>
                    <span><el-icon><View /></el-icon> {{ lesson.view_count }}</span>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-col>

        <el-col :span="8">
          <el-card class="stats-card">
            <h3>课程统计</h3>
            <el-statistic title="浏览次数" :value="course.view_count" />
            <el-statistic title="点赞数" :value="course.like_count" style="margin-top: 20px" />
            <el-statistic title="课时数量" :value="course.lessons?.length || 0" style="margin-top: 20px" />
            <el-button type="primary" @click="handleLike" style="margin-top: 20px; width: 100%">
              <el-icon><Star /></el-icon> 点赞课程
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { courseApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Clock, View, Star } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const course = ref(null)
const loading = ref(false)

const getDifficultyLabel = (difficulty) => {
  const labels = { beginner: '入门', intermediate: '进阶', advanced: '高级' }
  return labels[difficulty] || difficulty
}

const loadCourse = async () => {
  loading.value = true
  try {
    course.value = await courseApi.getCourseDetail(route.params.slug)
  } catch (error) {
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const goToLesson = (lesson) => {
  router.push(`/lessons/${lesson.slug}`)
}

const handleLike = async () => {
  try {
    await courseApi.likeCourse(route.params.slug)
    ElMessage.success('点赞成功')
    course.value.like_count++
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

onMounted(() => {
  loadCourse()
})
</script>

<style scoped>
.course-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.course-header h1 {
  margin: 0;
  display: inline-block;
  margin-right: 15px;
}

.course-description {
  margin-bottom: 30px;
}

.lessons-list {
  margin-top: 30px;
}

.lesson-item {
  cursor: pointer;
  transition: all 0.3s;
}

.lesson-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.lesson-item h4 {
  margin: 0 0 10px 0;
}

.lesson-meta {
  display: flex;
  gap: 20px;
  color: #999;
  margin-top: 10px;
}

.lesson-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stats-card h3 {
  margin-top: 0;
}
</style>
