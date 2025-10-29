<template>
  <el-dialog
    v-model="visible"
    title="AI助手"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="ai-chat">
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

        <div class="chat-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <span class="hint">Ctrl+Enter发送</span>
            <el-button type="primary" @click="sendMessage" :loading="loading">
              发送
            </el-button>
          </div>
        </div>
      </template>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const hasConfig = ref(false)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const sessionId = ref('')
const messagesContainer = ref(null)

onMounted(() => {
  checkConfig()
})

const checkConfig = async () => {
  try {
    await axios.get('/api/courses/ai-config/current/')
    hasConfig.value = true
    loadHistory()
  } catch (error) {
    hasConfig.value = false
  }
}

const loadHistory = async () => {
  if (!sessionId.value) {
    // 创建新会话
    sessionId.value = generateSessionId()
    return
  }

  try {
    const res = await axios.get('/api/courses/chat/history/', {
      params: { session_id: sessionId.value }
    })
    messages.value = res.data
    scrollToBottom()
  } catch (error) {
    console.error('加载历史失败', error)
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
    const res = await axios.post('/api/courses/chat/send/', {
      message: messageText,
      session_id: sessionId.value
    })

    sessionId.value = res.data.session_id

    messages.value.push({
      role: 'assistant',
      content: res.data.message,
      created_at: res.data.timestamp
    })

    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送失败: ' + (error.response?.data?.error || error.message))
    // 移除用户消息
    messages.value.pop()
  } finally {
    loading.value = false
  }
}

const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
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
  visible.value = false
  router.push('/settings/ai')
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.ai-chat {
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

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background-color: #409eff;
}

.message.assistant .message-avatar {
  background-color: #67c23a;
}

.message-content {
  max-width: 70%;
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
}

.message.user .message-text {
  background-color: #409eff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.chat-input {
  border-top: 1px solid #dcdfe6;
  padding-top: 15px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.hint {
  font-size: 12px;
  color: #909399;
}
</style>
