<template>
  <div class="notes-container">
    <el-card>
      <template #header>
        <div class="header">
          <h2>我的笔记</h2>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建笔记
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="我的笔记" name="my">
          <el-empty v-if="myNotes.length === 0" description="还没有创建笔记，快去学习课程并记录笔记吧！" />
          <div v-else class="notes-grid">
            <el-card
              v-for="note in myNotes"
              :key="note.id"
              class="note-card"
              shadow="hover"
            >
              <template #header>
                <div class="note-header">
                  <span class="lesson-title">{{ note.lesson_title }}</span>
                  <el-tag :type="note.is_public ? 'success' : 'info'" size="small">
                    {{ note.is_public ? '公开' : '私密' }}
                  </el-tag>
                </div>
              </template>
              <div class="note-content">{{ note.content }}</div>
              <div class="note-footer">
                <span class="time">{{ formatDate(note.created_at) }}</span>
                <div class="actions">
                  <el-button size="small" @click="editNote(note)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteNote(note)">删除</el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane label="公开笔记" name="public">
          <el-empty v-if="publicNotes.length === 0" description="暂无公开笔记" />
          <div v-else class="notes-grid">
            <el-card
              v-for="note in publicNotes"
              :key="note.id"
              class="note-card"
              shadow="hover"
            >
              <template #header>
                <div class="note-header">
                  <span class="lesson-title">{{ note.lesson_title }}</span>
                  <span class="author">by {{ note.username }}</span>
                </div>
              </template>
              <div class="note-content">{{ note.content }}</div>
              <div class="note-footer">
                <span class="time">{{ formatDate(note.created_at) }}</span>
                <el-button
                  size="small"
                  :icon="Star"
                  @click="likeNote(note)"
                >
                  {{ note.like_count }}
                </el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建/编辑笔记对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建笔记' : '编辑笔记'"
      width="600px"
    >
      <el-form
        ref="noteFormRef"
        :model="noteForm"
        :rules="noteFormRules"
        label-width="100px"
      >
        <el-form-item label="选择课时" prop="lesson" v-if="dialogMode === 'create'">
          <el-select
            v-model="noteForm.lesson"
            filterable
            placeholder="请选择课时"
            style="width: 100%"
          >
            <el-option
              v-for="lesson in availableLessons"
              :key="lesson.id"
              :label="lesson.title"
              :value="lesson.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="笔记内容" prop="content">
          <el-input
            v-model="noteForm.content"
            type="textarea"
            :rows="8"
            placeholder="记录你的学习心得..."
          />
        </el-form-item>
        <el-form-item label="是否公开">
          <el-switch v-model="noteForm.is_public" />
          <span class="tip">公开后其他用户可以查看</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNoteForm" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Star } from '@element-plus/icons-vue'
import axios from 'axios'

const activeTab = ref('my')
const myNotes = ref([])
const publicNotes = ref([])
const availableLessons = ref([])

const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const noteFormRef = ref()

const noteForm = reactive({
  lesson: null,
  content: '',
  is_public: false
})

const noteFormRules = {
  lesson: [
    { required: true, message: '请选择课时', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入笔记内容', trigger: 'blur' },
    { min: 10, message: '笔记内容至少10个字符', trigger: 'blur' }
  ]
}

const fetchMyNotes = async () => {
  try {
    const response = await axios.get('/api/courses/notes/', {
      params: { user: 'me' }
    })
    myNotes.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取笔记失败')
  }
}

const fetchPublicNotes = async () => {
  try {
    const response = await axios.get('/api/courses/notes/', {
      params: { is_public: true }
    })
    publicNotes.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取公开笔记失败')
  }
}

const fetchAvailableLessons = async () => {
  try {
    const response = await axios.get('/api/courses/lessons/')
    availableLessons.value = response.data.results || response.data
  } catch (error) {
    console.error('获取课时列表失败', error)
  }
}

const handleTabChange = (tab) => {
  if (tab === 'my') {
    fetchMyNotes()
  } else {
    fetchPublicNotes()
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetNoteForm()
  dialogVisible.value = true
  if (availableLessons.value.length === 0) {
    fetchAvailableLessons()
  }
}

const editNote = (note) => {
  dialogMode.value = 'edit'
  Object.assign(noteForm, {
    id: note.id,
    lesson: note.lesson,
    content: note.content,
    is_public: note.is_public
  })
  dialogVisible.value = true
}

const resetNoteForm = () => {
  Object.assign(noteForm, {
    lesson: null,
    content: '',
    is_public: false
  })
  noteFormRef.value?.resetFields()
}

const submitNoteForm = async () => {
  if (!noteFormRef.value) return
  
  await noteFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        await axios.post('/api/courses/notes/', noteForm)
        ElMessage.success('创建笔记成功')
      } else {
        await axios.put(`/api/courses/notes/${noteForm.id}/`, noteForm)
        ElMessage.success('更新笔记成功')
      }
      dialogVisible.value = false
      fetchMyNotes()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteNote = async (note) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条笔记吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/api/courses/notes/${note.id}/`)
    ElMessage.success('删除成功')
    fetchMyNotes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const likeNote = async (note) => {
  try {
    const response = await axios.post(`/api/courses/notes/${note.id}/like/`)
    note.like_count = response.data.like_count
    ElMessage.success('点赞成功')
  } catch (error) {
    ElMessage.error('点赞失败')
  }
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

onMounted(() => {
  fetchMyNotes()
})
</script>

<style scoped>
.notes-container {
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

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.note-card {
  height: 280px;
  display: flex;
  flex-direction: column;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lesson-title {
  font-weight: bold;
  color: #409eff;
}

.author {
  font-size: 12px;
  color: #909399;
}

.note-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 15px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.time {
  font-size: 12px;
  color: #909399;
}

.actions {
  display: flex;
  gap: 8px;
}

.tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}
</style>