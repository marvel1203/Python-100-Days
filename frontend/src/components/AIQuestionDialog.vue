<template>
  <el-dialog
    v-model="dialogVisible"
    title="AI问答"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <div class="ai-question-chat">
      <!-- AI配置状态 -->
      <div v-if="!hasConfig" class="config-notice">
        <el-alert
          title="请先配置AI服务"
          type="warning"
          :closable="false"
        >
          <template #default>
            <p>您还没有配置AI服务，请前往设置页面配置。</p>
            <el-button type="primary" size="small" @click="goToSettings">
              去配置
            </el-button>
          </template>
        </el-alert>
      </div>

      <!-- 聊天界面 -->
      <template v-else>
        <!-- 上下文信息 -->
        <div class="context-info" v-if="selectedText">
          <el-card shadow="never">
            <div class="context-header">
              <span class="context-title">选中文本：</span>
              <el-button
                size="small"
                :icon="DocumentCopy"
                @click="copySelectedText"
                title="复制选中文本"
              >
                复制
              </el-button>
            </div>
            <div class="selected-text">{{ selectedText }}</div>
          </el-card>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              {{ msg.role === 'user' ? '我' : 'AI' }}
            </div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime(msg.created_at) }}</div>
            </div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-avatar">AI</div>
            <div class="message-content">
              <div class="message-text">
                <el-icon class="is-loading"><Loading /></el-icon>
                思考中...
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            :placeholder="inputPlaceholder"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <div class="input-hints">
              <span class="hint">Ctrl+Enter发送</span>
              <span class="hint">支持上下文理解</span>
            </div>
            <div class="input-buttons">
              <el-button @click="resetChat">重置</el-button>
              <el-button type="primary" @click="sendMessage" :loading="loading">
                发送
              </el-button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedText: {
    type: String,
    default: ''
  },
  context: {
    type: String,
    default: ''
  },
  currentLesson: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['close', 'success'])

// 响应式数据
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('close', val)
})

const hasConfig = ref(false)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const sessionId = ref('')
const messagesContainer = ref(null)

// 计算属性
const inputPlaceholder = computed(() => {
  if (props.selectedText) {
    return '请输入你的问题（AI会结合选中文本的上下文来回答）...'
  }
  return '请输入你的问题...'
})

// 方法
onMounted(() => {
  checkConfig()
})

const checkConfig = async () => {
  try {
    await axios.get('/api/courses/ai-config/current/')
    hasConfig.value = true
  } catch (error) {
    hasConfig.value = false
  }
}

const initializeChat = async () => {
  if (!hasConfig.value) return

  // 生成新的会话ID
  sessionId.value = generateSessionId()

  // 如果有选中文本，自动发送第一个问题
  if (props.selectedText) {
    const initialQuestion = `关于"${props.selectedText}"，我有这样的问题：`
    inputMessage.value = initialQuestion
    await nextTick()
    // 不自动发送，让用户编辑问题
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    created_at: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const messageText = inputMessage.value
  inputMessage.value = ''
  loading.value = true

  await nextTick()
  scrollToBottom()

  try {
    const requestData = {
      message: messageText,
      session_id: sessionId.value
    }

    // 如果有上下文信息，添加到请求中
    if (props.selectedText) {
      requestData.extra_context = {
        selected_text: props.selectedText,
        full_context: props.context,
        lesson_title: props.currentLesson?.title,
        lesson_id: props.currentLesson?.id,
        question_type: 'text_selection'
      }
    }

    const res = await axios.post('/api/courses/chat/send/', requestData)

    sessionId.value = res.data.session_id

    messages.value.push({
      role: 'assistant',
      content: res.data.message,
      created_at: res.data.timestamp
    })

    await nextTick()
    scrollToBottom()

    // 发送成功后，可以在这里处理成功回调
    emit('success', {
      session_id: sessionId.value,
      messages: messages.value
    })
  } catch (error) {
    ElMessage.error('发送失败: ' + (error.response?.data?.error || error.message))
    // 移除用户消息
    messages.value.pop()
  } finally {
    loading.value = false
  }
}

const resetChat = () => {
  messages.value = []
  sessionId.value = generateSessionId()
  inputMessage.value = ''
  if (props.selectedText) {
    const initialQuestion = `关于"${props.selectedText}"，我有这样的问题：`
    inputMessage.value = initialQuestion
  }
}

const copySelectedText = async () => {
  if (!props.selectedText) return

  try {
    await navigator.clipboard.writeText(props.selectedText)
    ElMessage.success('已复制选中文本')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const generateSessionId = () => {
  return 'quick_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const goToSettings = () => {
  dialogVisible.value = false
  router.push('/settings/ai')
}

const handleClose = () => {
  dialogVisible.value = false
}

// 监听对话框显示状态
watch(dialogVisible, (newVal) => {
  if (newVal) {
    initializeChat()
  } else {
    // 对话框关闭时重置状态
    messages.value = []
    sessionId.value = ''
    inputMessage.value = ''
  }
})
</script>

<style scoped>
.ai-question-chat {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.config-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.context-info {
  margin-bottom: 16px;
}

.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.context-title {
  font-weight: bold;
  color: #409eff;
}

.selected-text {
  background-color: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
  line-height: 1.5;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
  font-size: 14px;
}

.message.user .message-avatar {
  background-color: #409eff;
}

.message.assistant .message-avatar {
  background-color: #67c23a;
}

.message-content {
  max-width: 75%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background-color: white;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message.user .message-text {
  background-color: #409eff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.chat-input {
  border-top: 1px solid #dcdfe6;
  padding-top: 12px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-hints {
  display: flex;
  gap: 16px;
}

.hint {
  font-size: 12px;
  color: #909399;
}

.input-buttons {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .selected-text {
    font-size: 14px;
    padding: 8px;
  }

  .message-content {
    max-width: 70%;
  }
}
</style>