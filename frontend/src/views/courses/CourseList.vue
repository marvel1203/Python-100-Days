<template>
  <div class="course-list">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>全部课程</h2>
        <el-form :inline="true" class="filter-form">
          <el-form-item label="难度">
            <el-select v-model="filters.difficulty" placeholder="全部难度" clearable>
              <el-option label="入门" value="beginner" />
              <el-option label="进阶" value="intermediate" />
              <el-option label="高级" value="advanced" />
            </el-select>
          </el-form-item>
          <el-form-item label="搜索">
            <el-input v-model="filters.search" placeholder="搜索课程" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadCourses">查询</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="course in courses" :key="course.id">
        <el-card class="course-card" @click="$router.push(`/courses/${course.slug}`)">
          <img :src="course.cover_image || '/default-course.svg'" class="course-cover" />
          <div class="course-info">
            <h3>{{ course.title }}</h3>
            <p class="day-range">{{ course.day_range }}</p>
            <p class="description">{{ course.description }}</p>
            <div class="meta">
              <el-tag size="small">{{ getDifficultyLabel(course.difficulty) }}</el-tag>
              <span><el-icon><View /></el-icon> {{ course.view_count }}</span>
              <span><el-icon><Star /></el-icon> {{ course.like_count }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row>
      <el-col :span="24" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadCourses"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { courseApi } from '@/api'
import { View, Star } from '@element-plus/icons-vue'

const courses = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(9)
const total = ref(0)
const filters = reactive({
  difficulty: '',
  search: '',
})

const getDifficultyLabel = (difficulty) => {
  const labels = {
    beginner: '入门',
    intermediate: '进阶',
    advanced: '高级',
  }
  return labels[difficulty] || difficulty
}

const loadCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      difficulty: filters.difficulty,
      search: filters.search,
    }
    const response = await courseApi.getCourses(params)
    courses.value = response.results
    total.value = response.count
  } catch (error) {
    console.error('加载课程失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-list {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-form {
  margin: 20px 0;
}

.course-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.course-cover {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.course-info {
  padding: 15px 0;
}

.course-info h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.day-range {
  color: #409eff;
  margin: 5px 0;
  font-weight: bold;
}

.description {
  color: #666;
  margin: 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
