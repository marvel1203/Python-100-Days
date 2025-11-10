<template>
  <div class="ai-chat-history">
    <el-card>
      <template #header>
        <div class="header">
          <h2>AI对话历史</h2>
          <div class="header-actions">
            <el-button @click="refreshHistory">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="danger" @click="clearAllHistory" :loading="clearing">
              <el-icon><Delete /></el-icon>
              清空历史
            </el-button>
          </div>
        </div>
      </template>

      <!-- 会话列表 -->
      <div class="sessions-container">
        <el-empty v-if="sessions.length === 0" description="暂无对话历史" />

        <div v-else class="sessions-grid">
          <el-card
            v-for="session in sessions"
            :key="session.session_id"
            class="session-card"
            shadow="hover"
            @click="openSession(session)"
          >
            <template #header>
              <div class="session-header">
                <div class="session-title">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>{{ formatSessionTitle(session) }}</span>
                </div>
                <div class="session-stats">
                  <el-tag size="small" type="info">
                    {{ session.message_count }}条消息
                  </el-tag>
                </div>
              </div>
            </template>

            <div class="session-preview">
              <div class="last-message">
                <span class="message-role">AI:</span>
                <span class="message-content">{{ formatMessagePreview(session.last_message) }}</span>
              </div>
              <div class="session-time">
                {{ formatDate(session.last_message_time) }}
              </div>
            </div>

            <div class="session-actions">
              <el-button size="small" @click="openSession(session)" text>
                查看详情
              </el-button>
              <el-button size="small" type="danger" @click="deleteSession(session.session_id)" text>
                删除
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 会话详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`对话详情 - ${formatSessionTitle(selectedSession)}`"
      width="900px"
      :close-on-click-modal="false"
    >
      <div class="session-detail">
        <!-- 会话信息 -->
        <div class="session-info" v-if="selectedSession">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="会话ID">
              {{ selectedSession.session_id }}
            </el-descriptions-item>
            <el-descriptions-item label="消息数量">
              {{ selectedSession.message_count }}
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatDate(selectedSession.first_message_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后活动">
              {{ formatDate(selectedSession.last_message_time) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div
            v-for="(message, index) in sessionMessages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-header">
              <span class="message-role">{{ message.role === 'user' ? '我' : 'AI' }}</span>
              <span class="message-time">{{ formatDate(message.created_at) }}</span>
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>

              <!-- 上下文信息 -->
              <div v-if="message.context && Object.keys(message.context).length > 0" class="message-context">
                <div class="context-label">上下文信息:</div>
                <div v-if="message.context.selected_text" class="context-item">
                  <strong>选中文本:</strong>
                  <span class="context-text">{{ message.context.selected_text }}</span>
                </div>
                <div v-if="message.context.lesson_title" class="context-item">
                  <strong>课程:</strong>
                  <span>{{ message.context.lesson_title }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="loadingMessages" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="dialog-actions">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="danger" @click="deleteSession(selectedSession?.session_id)" :loading="deletingSession">
            删除此会话
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Refresh, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const sessions = ref([])
const sessionMessages = ref([])
const loading = ref(false)
const loadingMessages = ref(false)
const clearing = ref(false)
const deletingSession = ref(false)

const dialogVisible = ref(false)
const selectedSession = ref(null)
const messagesContainer = ref(null)

// 方法
onMounted(() => {
  loadSessions()
})

const loadSessions = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/courses/chat/sessions/')
    sessions.value = response.data
  } catch (error) {
    ElMessage.error('加载会话列表失败')
    console.error('加载会话列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSessionMessages = async (sessionId) => {
  loadingMessages.value = true
  try {
    const response = await axios.get('/api/courses/chat/history/', {
      params: { session_id: sessionId }
    })
    sessionMessages.value = response.data
  } catch (error) {
    ElMessage.error('加载消息失败')
    console.error('加载消息失败:', error)
  } finally {
    loadingMessages.value = false
  }
}

const openSession = async (session) => {
  selectedSession.value = session
  await loadSessionMessages(session.session_id)
  dialogVisible.value = true
}

const deleteSession = async (sessionId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个会话吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    deletingSession.value = true
    await axios.delete(`/api/courses/chat/sessions/${sessionId}/delete_session/`)
    ElMessage.success('删除成功')
    loadSessions()

    if (dialogVisible.value) {
      dialogVisible.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    deletingSession.value = false
  }
}

const clearAllHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有对话历史吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    clearing.value = true
    await axios.delete('/api/courses/chat/sessions/clear_all/')
    ElMessage.success('清空成功')
    sessions.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  } finally {
    clearing.value = false
  }
}

const refreshHistory = () => {
  loadSessions()
}

const formatSessionTitle = (session) => {
  if (session.title) {
    return session.title
  }
  if (session.context?.lesson_title) {
    return `关于${session.context.lesson_title}`
  }
  return `会话 ${session.session_id.slice(-8)}`
}

const formatMessagePreview = (message) => {
  if (!message) return '暂无消息'
  const maxLength = 50
  return message.length > maxLength
    ? message.slice(0, maxLength) + '...'
    : message
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goToSettings = () => {
  router.push('/settings/ai')
}
</script>

<style scoped>
.ai-chat-history {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.session-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.session-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #409eff;
}

.session-stats {
  display: flex;
  gap: 8px;
}

.session-preview {
  margin: 16px 0;
}

.last-message {
  margin-bottom: 8px;
}

.message-role {
  font-weight: bold;
  color: #606266;
  margin-right: 8px;
}

.message-content {
  color: #909399;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.session-time {
  font-size: 12px;
  color: #909399;
}

.session-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

/* 会话详情样式 */
.session-detail {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.session-info {
  margin-bottom: 20px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  background-color: white;
}

.message.user {
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
}

.message.assistant {
  background-color: #f5fef0;
  border-left: 4px solid #67c23a;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-role {
  font-weight: bold;
  color: #409eff;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-text {
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-context {
  margin-top: 12px;
  padding: 8px;
  background-color: #fdf6e8;
  border: 1px solid #faecd8;
  border-radius: 4px;
}

.context-label {
  font-size: 12px;
  color: #e6a23c;
  font-weight: bold;
  margin-bottom: 4px;
}

.context-item {
  margin-top: 4px;
  font-size: 12px;
}

.context-item:first-child {
  margin-top: 0;
}

.context-text {
  background-color: #fff;
  padding: 2px 4px;
  border-radius: 2px;
  font-family: monospace;
  color: #303133;
}

.loading-container {
  padding: 20px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sessions-grid {
    grid-template-columns: 1fr;
  }

  .session-detail {
    height: 500px;
  }

  .messages-container {
    height: 300px;
  }
}
</style>