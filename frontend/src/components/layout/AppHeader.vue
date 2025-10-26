<template>
  <div class="header-container">
    <div class="logo">
      <router-link to="/">
        <h1>Python-100天</h1>
      </router-link>
    </div>
    <el-menu
      mode="horizontal"
      :default-active="activeIndex"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
      router
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/courses">课程</el-menu-item>
      <el-menu-item index="/exercises">练习</el-menu-item>
      <el-menu-item index="/progress" v-if="userStore.isLoggedIn">进度</el-menu-item>
      <el-menu-item index="/notes" v-if="userStore.isLoggedIn">笔记</el-menu-item>
    </el-menu>
    <div class="user-actions">
      <template v-if="userStore.isLoggedIn">
        <el-dropdown>
          <span class="user-name">
            <el-icon><User /></el-icon>
            {{ userStore.userInfo.username }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
        <el-button size="small" @click="$router.push('/register')">注册</el-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('退出成功')
  router.push('/')
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.logo {
  margin-right: 30px;
}

.logo a {
  color: #fff;
  text-decoration: none;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
}

.el-menu {
  flex: 1;
  border: none;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
