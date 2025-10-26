<template>
  <div class="sidebar">
    <el-menu :default-active="activeIndex" router>
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
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Document, EditPen, TrendCharts, Notebook } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)
</script>

<style scoped>
.sidebar {
  height: 100%;
}

.el-menu {
  border-right: none;
}
</style>
