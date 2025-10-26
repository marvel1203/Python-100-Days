<template>
  <div class="progress">
    <h2>学习进度</h2>
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="24">
        <el-card>
          <h3>学习统计</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总课时" :value="statistics.total_lessons" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已完成" :value="statistics.completed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="学习中" :value="statistics.in_progress" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="完成率" :value="statistics.completion_rate" suffix="%" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-table :data="progressList" style="margin-top: 20px">
      <el-table-column prop="lesson_title" label="课程" />
      <el-table-column prop="course_title" label="所属课程" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress_percentage" label="进度" width="120">
        <template #default="{ row }">
          {{ row.progress_percentage }}%
        </template>
      </el-table-column>
      <el-table-column prop="study_time" label="学习时长(分钟)" width="150" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { progressApi } from '@/api'

const progressList = ref([])
const statistics = ref({})
const loading = ref(false)

const getStatusLabel = (status) => {
  const labels = {
    not_started: '未开始',
    in_progress: '学习中',
    completed: '已完成',
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    not_started: 'info',
    in_progress: 'warning',
    completed: 'success',
  }
  return types[status] || ''
}

const loadProgress = async () => {
  loading.value = true
  try {
    const [progress, stats] = await Promise.all([
      progressApi.getProgress(),
      progressApi.getStatistics(),
    ])
    progressList.value = progress.results
    statistics.value = stats
  } catch (error) {
    console.error('加载进度失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProgress()
})
</script>
