<template>
  <teleport to="body">
    <transition name="fade">
      <div
        v-if="visible"
        class="text-selection-toolbar"
        :style="toolbarStyle"
        @mousedown.prevent
      >
        <el-button
          size="small"
          :icon="DocumentCopy"
          @click="handleCopy"
          title="复制选中文本"
        >
          复制
        </el-button>

        <el-button
          size="small"
          :icon="Memo"
          @click="handleNote"
          title="为选中文本添加笔记"
        >
          记笔记
        </el-button>

        <el-button
          size="small"
          :icon="ChatDotRound"
          @click="handleAIQuestion"
          title="向AI提问选中文本"
        >
          AI提问
        </el-button>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { DocumentCopy, Memo, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  disabledActions: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['copy', 'note', 'ai-question'])

// 响应式数据
const visible = ref(false)
const selectionInfo = ref({
  text: '',
  rect: { top: 0, left: 0, width: 0, height: 0 }
})

// 计算属性
const toolbarStyle = computed(() => {
  const { rect } = selectionInfo.value
  const toolbarHeight = 40 // 工具栏高度
  const offset = 8 // 偏移距离

  // position: fixed 是相对于视口的，所以不需要加 window.scrollY
  // 但为了防止工具栏超出屏幕顶部，需要做边界检查
  let top = rect.top - toolbarHeight - offset
  
  // 如果上方空间不足，显示在下方
  if (top < 0) {
    top = rect.bottom + offset
  }

  return {
    top: `${top}px`,
    left: `${rect.left + rect.width / 2 - 120}px` // 120是工具栏宽度的一半
  }
})

// 方法
const handleCopy = () => {
  if (props.disabledActions.includes('copy')) return

  navigator.clipboard.writeText(selectionInfo.value.text).then(() => {
    ElMessage.success('已复制到剪贴板')
    emit('copy', selectionInfo.value.text)
    hideToolbar()
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const handleNote = () => {
  if (props.disabledActions.includes('note')) return

  emit('note', {
    text: selectionInfo.value.text,
    context: getContext()
  })
  hideToolbar()
}

const handleAIQuestion = () => {
  if (props.disabledActions.includes('ai-question')) return

  emit('ai-question', {
    text: selectionInfo.value.text,
    context: getContext()
  })
  hideToolbar()
}

const getContext = () => {
  // 获取选中文本的上下文信息
  const selection = window.getSelection()
  if (!selection.rangeCount) return ''

  const range = selection.getRangeAt(0)
  const contextLength = 200 // 上下文字符长度

  // 获取包含选区的文本节点
  let startContainer = range.startContainer
  let endContainer = range.endContainer

  // 向前查找上下文
  let contextStart = range.startOffset
  let contextText = ''
  let tempRange = document.createRange()

  // 向前查找
  if (startContainer.nodeType === Node.TEXT_NODE) {
    const text = startContainer.textContent
    const beforeText = text.substring(0, range.startOffset)
    contextText = beforeText.slice(-contextLength / 2)
  }

  // 获取选中文本
  contextText += selection.toString()

  // 向后查找
  if (endContainer.nodeType === Node.TEXT_NODE) {
    const text = endContainer.textContent
    const afterText = text.substring(range.endOffset)
    contextText += afterText.substring(0, contextLength / 2)
  }

  return contextText.trim()
}

const showToolbar = (text, rect) => {
  selectionInfo.value = { text, rect }
  visible.value = true
}

const hideToolbar = () => {
  visible.value = false
  selectionInfo.value = { text: '', rect: { top: 0, left: 0, width: 0, height: 0 } }
}

const handleSelection = () => {
  const selection = window.getSelection()

  if (!selection.rangeCount) {
    hideToolbar()
    return
  }

  const selectedText = selection.toString().trim()

  if (selectedText.length < 1) {
    hideToolbar()
    return
  }

  // 获取选区的边界矩形
  const range = selection.getRangeAt(0)
  const rect = range.getBoundingClientRect()

  // 检查是否在工具栏内部
  const commonAncestor = range.commonAncestorContainer
  const validContainer = commonAncestor.nodeType === Node.ELEMENT_NODE
    ? commonAncestor
    : commonAncestor.parentNode

  if (validContainer && validContainer.closest('.text-selection-toolbar')) {
    return
  }

  // 只在选中文本长度合适时显示工具栏
  if (selectedText.length >= 1 && selectedText.length <= 1000) {
    showToolbar(selectedText, rect)
  } else {
    hideToolbar()
  }
}

const handleMouseDown = (event) => {
  // 如果点击的是工具栏内部，不隐藏
  if (event.target.closest('.text-selection-toolbar')) return
  
  hideToolbar()
}

const handleMouseUp = () => {
  // 鼠标释放时检查选择
  setTimeout(() => {
    handleSelection()
  }, 50)
}

const handleKeyUp = (event) => {
  // 支持 Shift + 箭头键的选择
  if (event.shiftKey && (event.key.startsWith('Arrow') || event.key === 'Home' || event.key === 'End')) {
    setTimeout(() => {
      handleSelection()
    }, 50)
  }
}

// 简单的防抖函数
const debounce = (fn, delay) => {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn(...args)
    }, delay)
  }
}

// 监听 selectionchange 事件，作为后备机制
const handleSelectionChange = debounce(() => {
  handleSelection()
}, 500)

const handleClick = (event) => {
  // 点击工具栏外部时隐藏
  if (!event.target.closest('.text-selection-toolbar')) {
    hideToolbar()
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('mousedown', handleMouseDown)
  // 使用 capture: true 确保捕获事件，防止被其他组件阻止冒泡
  document.addEventListener('mouseup', handleMouseUp, true)
  document.addEventListener('keyup', handleKeyUp)
  document.addEventListener('selectionchange', handleSelectionChange)
  document.addEventListener('click', handleClick)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleMouseDown)
  document.removeEventListener('mouseup', handleMouseUp, true)
  document.removeEventListener('keyup', handleKeyUp)
  document.removeEventListener('selectionchange', handleSelectionChange)
  document.removeEventListener('click', handleClick)
})
</script>

<style scoped>
.text-selection-toolbar {
  position: fixed;
  display: flex;
  gap: 8px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  padding: 8px;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}

.text-selection-toolbar .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
}

.text-selection-toolbar .el-button:hover {
  background-color: #f5f7fa;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 禁用状态样式 */
.text-selection-toolbar .el-button.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-selection-toolbar .el-button.is-disabled:hover {
  background-color: transparent;
}
</style>