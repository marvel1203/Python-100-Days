<template>
  <el-dialog
    v-model="visible"
    width="980px"
    class="code-runner-dialog"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <template #header>
      <div class="dialog-header">
        <div class="header-text">
          <h2>Python 代码实验室</h2>
          <p>即时验证想法，洞察运行输出；适合课程示例与互动练习场景。</p>
        </div>
        <el-tag type="info" effect="plain">Python 3.10 Runtime</el-tag>
      </div>
    </template>

    <div class="code-runner">
      <section class="editor-panel">
        <header class="panel-header">
          <div class="panel-title">
            <span class="dot dot-green"></span>
            <span class="dot dot-yellow"></span>
            <span class="dot dot-red"></span>
            <strong>main.py</strong>
          </div>
          <div class="panel-actions">
            <el-button type="primary" :icon="VideoPlay" :loading="running" @click="runCode">
              运行代码
            </el-button>
            <el-button link type="primary" :icon="Delete" @click="clearCode">清空</el-button>
          </div>
        </header>

        <div class="editor-shell">
          <div class="editor-gutter">
            <span v-for="line in lineNumbers" :key="line">{{ line }}</span>
          </div>
          <el-input
            v-model="code"
            type="textarea"
            :rows="18"
            resize="none"
            placeholder="输入 Python 代码..."
            class="code-editor"
          />
        </div>

        <footer class="hint-bar">
          <span>⌘ + Enter 运行</span>
          <span>代码会在隔离沙箱中执行</span>
        </footer>
      </section>

      <section class="output-panel">
        <header class="panel-header">
          <div>
            <strong>运行结果</strong>
            <p>最近运行时间：{{ lastRunLabel }}</p>
          </div>
          <el-tag v-if="result" :type="result.success ? 'success' : 'danger'">
            {{ result.success ? '运行成功' : '运行失败' }}
          </el-tag>
        </header>

        <div class="output-body" v-loading="running">
          <template v-if="result">
            <el-alert
              :type="result.success ? 'success' : 'error'"
              :title="result.success ? '执行完成' : '执行异常'"
              :description="metaDescription"
              :closable="false"
              class="result-alert"
              show-icon
            />

            <div v-if="result.output" class="output-block">
              <div class="block-title">标准输出</div>
              <pre>{{ result.output }}</pre>
            </div>

            <div v-if="result.error" class="error-block">
              <div class="block-title">错误输出</div>
              <pre>{{ result.error }}</pre>
            </div>

            <ul class="meta-list">
              <li><span>执行耗时</span><strong>{{ result.execution_time }}s</strong></li>
              <li><span>触发于</span><strong>{{ lastRunLabel }}</strong></li>
            </ul>
          </template>

          <el-empty
            v-else
            description="编写代码后点击运行，即可查看输出与性能指标"
            :image-size="160"
            class="empty-state"
          >
            <template #image>
              <img src="https://img.alicdn.com/imgextra/i3/O1CN01bB6p5Q1n6Qt1zAr72_!!6000000005011-55-tps-160-160.svg" alt="空状态" />
            </template>
          </el-empty>
        </div>
      </section>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { VideoPlay, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const defaultCode = `# 输入 Python 代码，点击右上角运行按钮
from datetime import datetime

print("Hello, Python 100 Days!")
print("当前时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 示例：快速计算平方和
total = sum(i * i for i in range(10))
print("平方和:", total)
`

const code = ref(defaultCode)

const result = ref(null)
const running = ref(false)
const lastRunAt = ref(null)

const lineNumbers = computed(() => {
  const lines = code.value.split('\n').length
  return Array.from({ length: lines }, (_, index) => index + 1)
})

const metaDescription = computed(() => {
  if (!result.value) return ''
  return result.value.success ? '代码已成功执行，可继续优化你的脚本。' : '请检查代码逻辑或语法，修复后再次尝试。'
})

const lastRunLabel = computed(() => {
  if (!lastRunAt.value) return '尚未运行'
  return new Intl.DateTimeFormat('zh-CN', {
    hour12: false,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(lastRunAt.value)
})

const handleKeydown = (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    runCode()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

watch(
  () => visible.value,
  (val) => {
    if (val) {
      setTimeout(() => {
        const textarea = document.querySelector('.code-editor textarea')
        textarea?.focus()
      }, 200)
    }
  }
)

const runCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }

  running.value = true
  result.value = null

  try {
    const res = await axios.post('/api/exercises/exercises/run_code/', {
      code: code.value
    })
    result.value = res.data
    lastRunAt.value = new Date()
  } catch (error) {
    ElMessage.error('运行失败: ' + (error.response?.data?.error || error.message))
  } finally {
    running.value = false
  }
}

const clearCode = () => {
  code.value = ''
  result.value = null
  lastRunAt.value = null
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.code-runner-dialog :deep(.el-dialog__header) {
  padding-bottom: 0;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}

.dialog-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #0f172a;
}

.dialog-header p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.code-runner {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 24px;
  min-height: 540px;
}

@media (max-width: 1100px) {
  .code-runner {
    grid-template-columns: 1fr;
  }
}

.editor-panel,
.output-panel {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 255, 0.9));
  border-radius: 22px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.14);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.panel-header strong {
  display: block;
  font-size: 16px;
  color: #0f172a;
}

.panel-header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #94a3b8;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #475569;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-flex;
}

.dot-green {
  background: #10b981;
}

.dot-yellow {
  background: #f59e0b;
}

.dot-red {
  background: #ef4444;
}

.editor-shell {
  flex: 1;
  display: flex;
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.12);
}

.editor-gutter {
  width: 48px;
  padding: 16px 0 16px 16px;
  background: rgba(15, 23, 42, 0.92);
  color: rgba(148, 163, 184, 0.65);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.4;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
}

.code-editor {
  flex: 1;
  background: transparent;
  border: none;
}

.code-editor :deep(textarea) {
  height: 100%;
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  padding: 16px 18px;
  caret-color: #38bdf8;
}

.code-editor :deep(textarea::placeholder) {
  color: rgba(148, 163, 184, 0.45);
}

.code-editor :deep(textarea:focus) {
  outline: none;
  box-shadow: none;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.hint-bar {
  margin-top: 14px;
  font-size: 11px;
  color: #94a3b8;
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.output-body {
  flex: 1;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.04);
  padding: 18px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-alert {
  border-radius: 16px;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.12);
}

.output-block,
.error-block {
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  box-shadow: inset 0 0 0 1px rgba(226, 232, 240, 0.7);
}

.error-block {
  background: #fff5f5;
  box-shadow: inset 0 0 0 1px rgba(248, 113, 113, 0.25);
}

.block-title {
  margin: 0;
  padding: 12px 16px;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid rgba(226, 232, 240, 0.7);
}

.error-block .block-title {
  color: #ef4444;
  border-bottom: 1px solid rgba(248, 113, 113, 0.28);
}

.output-block pre,
.error-block pre {
  margin: 0;
  padding: 16px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  color: #0f172a;
}

.error-block pre {
  color: #b91c1c;
}

.meta-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 18px;
  font-size: 12px;
  color: #475569;
}

.meta-list li {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-list strong {
  font-size: 14px;
  color: #0f172a;
}

.output-section {
  border-left: 1px solid #dcdfe6;
  padding-left: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.output-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.output-block,
.error-block {
  margin-bottom: 15px;
}

.block-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #606266;
}

.output-block pre {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-block pre {
  background-color: #fef0f0;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #fbc4c4;
  color: #f56c6c;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.meta-info {
  color: #909399;
  font-size: 12px;
}
</style>
