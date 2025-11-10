<template>
  <el-dialog
    v-model="dialogVisible"
    title="快速记笔记"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="noteFormRef"
      :model="noteForm"
      :rules="noteFormRules"
      label-width="80px"
    >
      <el-form-item label="选中文本">
        <el-input
          v-model="noteForm.selectedText"
          type="textarea"
          :rows="3"
          readonly
          :autosize="{ minRows: 3, maxRows: 5 }"
        />
      </el-form-item>

      <el-form-item label="笔记内容" prop="content">
        <el-input
          v-model="noteForm.content"
          type="textarea"
          :rows="6"
          placeholder="记录你对这段文本的理解、感悟或问题..."
          :autosize="{ minRows: 6, maxRows: 10 }"
        />
      </el-form-item>

      <el-form-item label="关联课时">
        <el-input
          v-model="currentLessonTitle"
          readonly
          placeholder="当前课时"
        />
      </el-form-item>

      <el-form-item label="是否公开">
        <el-switch
          v-model="noteForm.is_public"
          active-text="公开"
          inactive-text="私密"
        />
        <div class="form-tip">公开后其他用户可以查看你的笔记</div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          保存笔记
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { noteApi } from '@/api'

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
  set: (value) => emit('close', value)
})

const submitting = ref(false)
const noteFormRef = ref()

const noteForm = reactive({
  selectedText: props.selectedText,
  content: '',
  is_public: false,
  context: props.context
})

const currentLessonTitle = computed(() => {
  return props.currentLesson?.title || '未知课时'
})

// 表单验证规则
const noteFormRules = {
  content: [
    { required: true, message: '请输入笔记内容', trigger: 'blur' },
    { min: 5, message: '笔记内容至少5个字符', trigger: 'blur' }
  ]
}

// 方法
const resetForm = () => {
  Object.assign(noteForm, {
    selectedText: props.selectedText,
    content: '',
    is_public: false,
    context: props.context
  })
  noteFormRef.value?.resetFields()
}

const handleCancel = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!noteFormRef.value) return

  await noteFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const noteData = {
        lesson: props.currentLesson?.id,
        content: noteForm.content,
        is_public: noteForm.is_public
      }

      await noteApi.createNote(noteData)
      ElMessage.success('笔记创建成功')
      emit('success', noteData)
      dialogVisible.value = false
    } catch (error) {
      console.error('创建笔记失败:', error)
      ElMessage.error(error.response?.data?.detail || '创建笔记失败')
    } finally {
      submitting.value = false
    }
  })
}

// 监听props变化
import { watch } from 'vue'
watch(
  () => props.selectedText,
  (newText) => {
    noteForm.selectedText = newText
  }
)

watch(
  () => props.context,
  (newContext) => {
    noteForm.context = newContext
  }
)

// 组件挂载时重置表单
import { onMounted } from 'vue'
onMounted(() => {
  resetForm()
})
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 选中文本的样式 */
:deep(.el-textarea.is-controls) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  cursor: not-allowed;
}

:deep(.el-textarea.is-controls .el-textarea__inner) {
  background-color: #f5f7fa;
  color: #909399;
  cursor: not-allowed;
}
</style>