<template>
  <aside class="sidebar">
    <section class="sidebar-hero">
      <div class="hero-badge">进阶导航</div>
      <h2>Python 100 天</h2>
      <p>精选课程与实战练习，助你稳步提升。</p>
      <el-button type="primary" text class="hero-action" @click="goDailyTask">
        今日学习任务
      </el-button>
    </section>

    <el-menu :default-active="activeIndex" router class="sidebar-menu">
      <el-menu-item index="/courses">
        <el-icon><Document /></el-icon>
        <span>全部课程</span>
      </el-menu-item>
      <el-menu-item index="/exercises">
        <el-icon><EditPen /></el-icon>
        <span>练习题库</span>
      </el-menu-item>
      <el-menu-item index="/progress" v-if="userStore.isLoggedIn">
        <el-icon><TrendCharts /></el-icon>
        <span>学习进度</span>
      </el-menu-item>
      <el-menu-item index="/notes" v-if="userStore.isLoggedIn">
        <el-icon><Notebook /></el-icon>
        <span>我的笔记</span>
      </el-menu-item>
      <el-menu-item index="/settings/ai" v-if="userStore.isLoggedIn">
        <el-icon><ChatDotRound /></el-icon>
        <span>AI助手配置</span>
      </el-menu-item>
    </el-menu>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Document, EditPen, TrendCharts, Notebook, ChatDotRound } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)

const goDailyTask = () => {
  if (userStore.isLoggedIn) {
    router.push('/progress')
  } else {
    router.push('/courses')
  }
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  padding: 32px 22px 22px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-hero {
  padding: 22px 20px;
  border-radius: 22px;
  background: linear-gradient(140deg, rgba(56, 189, 248, 0.14) 0%, rgba(14, 165, 233, 0.08) 35%, rgba(236, 72, 153, 0.12) 100%);
  box-shadow: 0 24px 45px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(14px);
  color: #132238;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: #0f172a;
  margin-bottom: 12px;
}

.hero-badge::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #60a5fa);
}

.sidebar-hero h2 {
  font-size: 22px;
  margin-bottom: 6px;
}

.sidebar-hero p {
  font-size: 13px;
  color: rgba(19, 34, 56, 0.72);
  margin-bottom: 18px;
  line-height: 1.5;
}

.hero-action {
  padding: 0;
  font-weight: 600;
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.hero-action:hover {
  color: #0284c7;
}

.sidebar-menu {
  border-right: none;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(249, 250, 253, 0.92));
  box-shadow: 0 18px 32px rgba(31, 41, 55, 0.08);
  padding: 12px 10px;
}

.sidebar-menu :deep(.el-menu-item) {
  border-radius: 14px;
  margin: 6px 0;
  height: 48px;
  font-weight: 500;
  color: #3b4656;
  transition: all 0.2s ease;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(56, 189, 248, 0.18), rgba(236, 72, 153, 0.18));
  color: #0284c7;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(56, 189, 248, 0.12);
  color: #0284c7;
}
</style>
