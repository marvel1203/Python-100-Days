<template>
  <div class="floating-container">
    <!-- 主悬浮按钮 -->
    <el-button 
      type="primary" 
      :icon="expanded ? Close : Plus"
      circle
      size="large"
      class="main-fab"
      @click="toggleMenu"
    />

    <!-- 展开的菜单 -->
    <transition-group name="fab-menu">
      <el-button
        v-if="expanded"
        key="code"
        type="success"
        :icon="Document"
        circle
        class="fab-item fab-code"
        @click="openCodeRunner"
      >
        <el-tooltip content="代码运行" placement="left" />
      </el-button>

      <el-button
        v-if="expanded"
        key="ai"
        type="warning"
        :icon="ChatDotRound"
        circle
        class="fab-item fab-ai"
        @click="openAIChat"
      >
        <el-tooltip content="AI助手" placement="left" />
      </el-button>
    </transition-group>

    <!-- 代码运行对话框 -->
    <CodeRunnerDialog v-model="codeRunnerVisible" />

    <!-- AI对话对话框 -->
    <AIChatDialog v-model="aiChatVisible" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, Close, Document, ChatDotRound } from '@element-plus/icons-vue'
import CodeRunnerDialog from './CodeRunnerDialog.vue'
import AIChatDialog from './AIChatDialog.vue'

const expanded = ref(false)
const codeRunnerVisible = ref(false)
const aiChatVisible = ref(false)

const toggleMenu = () => {
  expanded.value = !expanded.value
}

const openCodeRunner = () => {
  codeRunnerVisible.value = true
  expanded.value = false
}

const openAIChat = () => {
  aiChatVisible.value = true
  expanded.value = false
}
</script>

<style scoped>
.floating-container {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 1000;
  display: flex;
  flex-direction: column-reverse;
  align-items: flex-end;
  gap: 15px;
}

.main-fab {
  width: 60px;
  height: 60px;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-fab:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.fab-item {
  width: 50px;
  height: 50px;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.fab-code {
  transform-origin: center bottom;
}

.fab-ai {
  transform-origin: center bottom;
}

/* 动画 */
.fab-menu-enter-active,
.fab-menu-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-menu-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0);
}

.fab-menu-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0);
}

.fab-code.fab-menu-enter-active {
  transition-delay: 0.05s;
}

.fab-ai.fab-menu-enter-active {
  transition-delay: 0.1s;
}
</style>
