<template>
  <div class="exercise-detail" v-loading="loading">
    <el-card v-if="exercise" class="exercise-card">
      <!-- 题目信息 -->
      <template #header>
        <div class="header">
          <h1>{{ exercise.title }}</h1>
          <div class="meta">
            <el-tag :type="difficultyColor">{{ difficultyLabel }}</el-tag>
            <el-tag v-for="tag in exercise.tags_list" :key="tag" type="info">{{ tag }}</el-tag>
            <span class="stat">通过率: {{ exercise.acceptance_rate }}%</span>
          </div>
        </div>
      </template>

      <!-- 问题描述 -->
      <div class="problem-section">
        <h3>题目描述</h3>
        <div class="problem-description" v-html="renderedProblem"></div>
      </div>

      <!-- 示例 -->
      <div class="examples-section" v-if="exercise.examples">
        <h3>示例</h3>
        <div class="example" v-for="(example, index) in exercise.examples" :key="index">
          <p><strong>示例 {{ index + 1 }}:</strong></p>
          <pre class="example-code">输入: {{ example.input }}
输出: {{ example.output }}</pre>
          <p v-if="example.explanation" class="explanation">{{ example.explanation }}</p>
        </div>
      </div>

      <!-- 提示 -->
      <div class="hints-section" v-if="exercise.hints">
        <h3>提示</h3>
        <ul>
          <li v-for="(hint, index) in exercise.hints" :key="index">{{ hint }}</li>
        </ul>
      </div>
    </el-card>

    <!-- 代码编辑器和运行区域 -->
    <el-card class="code-section">
      <template #header>
        <div class="code-header">
          <span>代码编辑器</span>
          <div class="actions">
            <el-select v-model="editorTheme" size="small" style="width: 120px; margin-right: 10px">
              <el-option label="暗色主题" value="vs-dark" />
              <el-option label="亮色主题" value="vs" />
              <el-option label="高对比度" value="hc-black" />
            </el-select>
            <el-button type="primary" @click="runCode" :loading="running" :icon="VideoPlay">
              运行代码
            </el-button>
            <el-button @click="submitCode" :loading="submitting" :icon="Upload">
              提交代码
            </el-button>
            <el-button @click="resetCode" :icon="RefreshRight">重置</el-button>
          </div>
        </div>
      </template>

      <!-- Monaco编辑器 -->
      <code-editor
        v-model="code"
        :theme="editorTheme"
        language="python"
        height="500px"
        ref="codeEditorRef"
      />

      <!-- 输入区域 -->
      <div class="input-section">
        <h4>标准输入 (可选)</h4>
        <el-input
          v-model="stdin"
          type="textarea"
          :rows="3"
          placeholder="如果程序需要输入，请在这里输入测试数据..."
        />
      </div>

      <!-- 运行结果 -->
      <div class="output-section" v-if="output">
        <h4>运行结果</h4>
        <el-alert
          :type="output.success ? 'success' : 'error'"
          :title="output.success ? '运行成功' : '运行失败'"
          :closable="false"
        >
          <template #default>
            <div class="output-info">
              <span>执行时间: {{ output.execution_time }}s</span>
            </div>
          </template>
        </el-alert>
        <pre class="output-content" :class="{ error: !output.success }">{{ output.output || output.error }}</pre>
      </div>
    </el-card>

    <!-- 提交历史 -->
    <el-card class="history-section" v-if="isAuthenticated">
      <template #header>
        <h3>提交历史</h3>
      </template>
      <el-table :data="submissions" v-loading="loadingSubmissions">
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_time" label="执行时间" width="120">
          <template #default="{ row }">
            {{ row.execution_time }}ms
          </template>
        </el-table-column>
        <el-table-column prop="memory" label="内存" width="120">
          <template #default="{ row }">
            {{ row.memory }}KB
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewSubmission(row)">查看代码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, Upload, RefreshRight } from '@element-plus/icons-vue'
import { exerciseApi } from '@/api'
import { useUserStore } from '@/stores/user'
import CodeEditor from '@/components/CodeEditor.vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const route = useRoute()
const userStore = useUserStore()

const exercise = ref(null)
const loading = ref(false)
const code = ref(`# 在这里编写你的Python代码\ndef solution():\n    pass\n\nif __name__ == '__main__':\n    solution()\n`)
const stdin = ref('')
const output = ref(null)
const running = ref(false)
const submitting = ref(false)
const editorTheme = ref('vs-dark')
const codeEditorRef = ref(null)
const submissions = ref([])
const loadingSubmissions = ref(false)

const isAuthenticated = computed(() => userStore.isAuthenticated)

// Markdown渲染器
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

const renderedProblem = computed(() => {
  return exercise.value ? md.render(exercise.value.problem_description) : ''
})

const difficultyLabel = computed(() => {
  const labels = { easy: '简单', medium: '中等', hard: '困难' }
  return labels[exercise.value?.difficulty] || exercise.value?.difficulty
})

const difficultyColor = computed(() => {
  const colors = { easy: 'success', medium: 'warning', hard: 'danger' }
  return colors[exercise.value?.difficulty] || ''
})

// 加载练习详情
const loadExercise = async () => {
  loading.value = true
  try {
    exercise.value = await exerciseApi.getExerciseDetail(route.params.slug)
    
    // 如果有初始代码，使用初始代码
    if (exercise.value.starter_code) {
      code.value = exercise.value.starter_code
    }
  } catch (error) {
    ElMessage.error('加载练习失败')
  } finally {
    loading.value = false
  }
}

// 运行代码
const runCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码')
    return
  }

  running.value = true
  output.value = null

  try {
    const result = await exerciseApi.runCode({
      code: code.value,
      stdin: stdin.value
    })
    
    output.value = result
    
    if (result.success) {
      ElMessage.success('代码运行成功')
    } else {
      ElMessage.error('代码运行失败')
    }
  } catch (error) {
    ElMessage.error('运行失败: ' + (error.response?.data?.error || error.message))
    output.value = {
      success: false,
      error: error.response?.data?.error || error.message,
      execution_time: 0
    }
  } finally {
    running.value = false
  }
}

// 提交代码
const submitCode = async () => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }

  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码')
    return
  }

  submitting.value = true
  try {
    await exerciseApi.submitCode(exercise.value.slug, {
      code: code.value,
      language: 'python'
    })
    
    ElMessage.success('提交成功')
    loadSubmissions() // 重新加载提交历史
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 重置代码
const resetCode = () => {
  if (exercise.value?.starter_code) {
    code.value = exercise.value.starter_code
  } else {
    code.value = `# 在这里编写你的Python代码\ndef solution():\n    pass\n\nif __name__ == '__main__':\n    solution()\n`
  }
  output.value = null
  stdin.value = ''
  ElMessage.success('已重置代码')
}

// 加载提交历史
const loadSubmissions = async () => {
  if (!isAuthenticated.value) return
  
  loadingSubmissions.value = true
  try {
    const data = await exerciseApi.getSubmissions({
      exercise: exercise.value.id
    })
    submissions.value = data.results || []
  } catch (error) {
    console.error('加载提交历史失败', error)
  } finally {
    loadingSubmissions.value = false
  }
}

// 查看提交
const viewSubmission = (submission) => {
  code.value = submission.code
  ElMessage.info('已加载提交的代码')
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'accepted': 'success',
    'wrong_answer': 'danger',
    'runtime_error': 'warning',
    'time_limit_exceeded': 'info',
    'pending': 'info'
  }
  return types[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    'accepted': '通过',
    'wrong_answer': '答案错误',
    'runtime_error': '运行错误',
    'time_limit_exceeded': '超时',
    'pending': '待判题'
  }
  return labels[status] || status
}

onMounted(() => {
  loadExercise()
  if (isAuthenticated.value) {
    loadSubmissions()
  }
})
</script>

<style scoped>
.exercise-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.exercise-card {
  margin-bottom: 20px;
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stat {
  color: #909399;
  font-size: 14px;
}

.problem-section,
.examples-section,
.hints-section {
  margin-bottom: 30px;
}

.problem-section h3,
.examples-section h3,
.hints-section h3 {
  margin-bottom: 15px;
  font-size: 18px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 5px;
}

.problem-description {
  line-height: 1.8;
  font-size: 15px;
}

.example {
  margin-bottom: 20px;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.example-code {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  margin: 10px 0;
  overflow-x: auto;
}

.explanation {
  color: #606266;
  font-style: italic;
}

.code-section {
  margin-bottom: 20px;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.input-section {
  margin-top: 20px;
}

.input-section h4 {
  margin-bottom: 10px;
}

.output-section {
  margin-top: 20px;
}

.output-section h4 {
  margin-bottom: 10px;
}

.output-info {
  margin-top: 5px;
  font-size: 13px;
}

.output-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.output-content.error {
  color: #f56c6c;
}

.history-section {
  margin-bottom: 20px;
}
</style>
