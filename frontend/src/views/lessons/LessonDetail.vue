<template>
  <div class="lesson-detail" v-loading="loading">
    <el-card v-if="lesson">
      <template #header>
        <div class="lesson-header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/courses' }">课程</el-breadcrumb-item>
            <el-breadcrumb-item :to="{ path: `/courses/${lesson.course_slug}` }">
              {{ lesson.course_title }}
            </el-breadcrumb-item>
            <el-breadcrumb-item>{{ lesson.title }}</el-breadcrumb-item>
          </el-breadcrumb>
          <h1>Day{{ lesson.day_number.toString().padStart(2, '0') }} - {{ lesson.title }}</h1>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="18">
          <div class="lesson-content">
            <MarkdownViewer :content="lesson.content" />
          </div>

          <div class="lesson-resources" v-if="lesson.resources && lesson.resources.length > 0">
            <h3>课程资源</h3>
            <el-table :data="lesson.resources">
              <el-table-column prop="title" label="资源名称" />
              <el-table-column prop="file_type" label="类型" width="100" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="downloadResource(row)">
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <el-col :span="6">
          <el-card class="sidebar-card">
            <h3>学习信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="预计时长">
                {{ lesson.estimated_time }}分钟
              </el-descriptions-item>
              <el-descriptions-item label="浏览次数">
                {{ lesson.view_count }}
              </el-descriptions-item>
              <el-descriptions-item label="点赞数">
                {{ lesson.like_count }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="actions" style="margin-top: 20px">
              <el-button type="primary" @click="markAsCompleted" style="width: 100%">
                标记为已完成
              </el-button>
              <el-button @click="handleLike" style="width: 100%; margin-top: 10px">
                <el-icon><Star /></el-icon> 点赞
              </el-button>
            </div>

            <div class="code-link" v-if="lesson.code_url" style="margin-top: 20px">
              <el-button type="success" @click="openCodeUrl" style="width: 100%">
                <el-icon><Link /></el-icon> 查看代码
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { courseApi, progressApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Star, Link } from '@element-plus/icons-vue'
import MarkdownViewer from '@/components/MarkdownViewer.vue'

const route = useRoute()
const lesson = ref(null)
const loading = ref(false)

const loadLesson = async () => {
  loading.value = true
  try {
    lesson.value = await courseApi.getLessonDetail(route.params.slug)
  } catch (error) {
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const markAsCompleted = async () => {
  try {
    await progressApi.updateProgress(lesson.value.id, { status: 'completed' })
    ElMessage.success('已标记为完成')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleLike = async () => {
  try {
    await courseApi.likeLesson(route.params.slug)
    ElMessage.success('点赞成功')
    lesson.value.like_count++
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

const downloadResource = (resource) => {
  window.open(resource.file, '_blank')
}

const openCodeUrl = () => {
  window.open(lesson.value.code_url, '_blank')
}

onMounted(() => {
  loadLesson()
})
</script>

<style scoped>
.lesson-header h1 {
  margin: 15px 0;
}

.lesson-content {
  padding: 20px 0;
}

.lesson-resources {
  margin-top: 30px;
}

.sidebar-card h3 {
  margin-top: 0;
}
</style>
