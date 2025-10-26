<template>
  <div class="exercise-list">
    <h2>练习题库</h2>
    <el-form :inline="true" class="filter-form">
      <el-form-item label="难度">
        <el-select v-model="filters.difficulty" placeholder="全部难度" clearable>
          <el-option label="简单" value="easy" />
          <el-option label="中等" value="medium" />
          <el-option label="困难" value="hard" />
        </el-select>
      </el-form-item>
      <el-form-item label="搜索">
        <el-input v-model="filters.search" placeholder="搜索练习" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadExercises">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="exercises" v-loading="loading">
      <el-table-column prop="title" label="题目" />
      <el-table-column prop="difficulty" label="难度" width="100">
        <template #default="{ row }">
          <el-tag :type="getDifficultyType(row.difficulty)">
            {{ getDifficultyLabel(row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="acceptance_rate" label="通过率" width="120">
        <template #default="{ row }">
          {{ (row.acceptance_rate * 100).toFixed(1) }}%
        </template>
      </el-table-column>
      <el-table-column prop="submit_count" label="提交次数" width="120" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="goToExercise(row)">
            开始练习
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      @current-change="loadExercises"
      style="margin-top: 20px; text-align: center"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { exerciseApi } from '@/api'

const router = useRouter()
const exercises = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({
  difficulty: '',
  search: '',
})

const getDifficultyLabel = (difficulty) => {
  const labels = { easy: '简单', medium: '中等', hard: '困难' }
  return labels[difficulty] || difficulty
}

const getDifficultyType = (difficulty) => {
  const types = { easy: 'success', medium: 'warning', hard: 'danger' }
  return types[difficulty] || ''
}

const loadExercises = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      difficulty: filters.difficulty,
      search: filters.search,
    }
    const response = await exerciseApi.getExercises(params)
    exercises.value = response.results
    total.value = response.count
  } catch (error) {
    console.error('加载练习失败:', error)
  } finally {
    loading.value = false
  }
}

const goToExercise = (exercise) => {
  router.push(`/exercises/${exercise.slug}`)
}

onMounted(() => {
  loadExercises()
})
</script>

<style scoped>
.exercise-list {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-form {
  margin: 20px 0;
}
</style>
