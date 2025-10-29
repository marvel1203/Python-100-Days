<template>
  <header class="header-container">
    <div class="header-inner">
      <router-link to="/" class="brand">
        <div class="brand-mark">PY</div>
        <div class="brand-text">
          <h1>Python 100 天</h1>
          <p class="brand-slogan">系统化·场景化·真实企业级项目实践</p>
        </div>
      </router-link>
      <el-menu
        mode="horizontal"
        :default-active="activeIndex"
        class="nav-menu"
        text-color="#64748b"
        active-text-color="#0f172a"
        router
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/courses">课程</el-menu-item>
        <el-menu-item index="/exercises">练习</el-menu-item>
        <el-menu-item index="/progress" v-if="userStore.isLoggedIn">进度</el-menu-item>
        <el-menu-item index="/notes" v-if="userStore.isLoggedIn">笔记</el-menu-item>
        <el-menu-item index="/admin/users" v-if="userStore.isAdmin">
          <el-icon><Setting /></el-icon>
          控制台
        </el-menu-item>
      </el-menu>
      <div class="global-search">
        <el-autocomplete
          v-model="searchKeyword"
          class="search-input"
          :fetch-suggestions="fetchCourseSuggestions"
          placeholder="快速搜索课程"
          :debounce="300"
          :loading="searchLoading"
          clearable
          :trigger-on-focus="false"
          @select="handleCourseSelect"
          @clear="handleSearchClear"
          @keyup.enter="handleSearchEnter"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #default="{ item }">
            <div class="search-option">
              <span class="option-title">{{ item.value }}</span>
              <span class="option-meta">
                {{ item.dayRange }} · {{ getDifficultyLabel(item.difficulty) }}
              </span>
            </div>
          </template>
        </el-autocomplete>
      </div>
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <el-dropdown>
            <span class="user-name">
              <el-icon><User /></el-icon>
              <div class="user-meta">
                <strong>{{ userStore.userInfo.username }}</strong>
                <span>欢迎回来</span>
              </div>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goAISettings">
                  <el-icon><ChatDotRound /></el-icon>
                  AI助手配置
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" class="ghost-btn" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Setting, ChatDotRound, Search } from '@element-plus/icons-vue'
import { courseApi } from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)

const searchKeyword = ref('')
const searchLoading = ref(false)
let lastQueryToken = 0

const difficultyLabels = {
  beginner: '入门',
  intermediate: '进阶',
  advanced: '高级',
}

const getDifficultyLabel = (value) => difficultyLabels[value] || '综合'

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('退出成功')
  router.push('/')
}

const goAISettings = () => {
  router.push('/settings/ai')
}

const fetchCourseSuggestions = async (queryString, cb) => {
  const keyword = queryString.trim()
  if (!keyword) {
    cb([])
    return
  }

  const token = Date.now()
  lastQueryToken = token
  searchLoading.value = true

  try {
    const response = await courseApi.getCourses({ search: keyword, page_size: 8 })
    if (lastQueryToken !== token) {
      return
    }
    const data = response?.results || response || []
    const suggestions = data.map((course) => ({
      value: course.title,
      slug: course.slug,
      dayRange: course.day_range,
      difficulty: course.difficulty,
      route: `/courses/${course.slug}`,
    }))
    cb(suggestions)
  } catch (error) {
    console.error('搜索课程失败', error)
    cb([])
  } finally {
    if (lastQueryToken === token) {
      searchLoading.value = false
    }
  }
}

const handleCourseSelect = (item) => {
  if (item?.route) {
    router.push(item.route)
  } else if (item?.slug) {
    router.push(`/courses/${item.slug}`)
  } else if (item?.value) {
    router.push({ path: '/courses', query: { search: item.value } })
  }
  searchKeyword.value = ''
}

const handleSearchEnter = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    return
  }
  router.push({ path: '/courses', query: { search: keyword } })
}

const handleSearchClear = () => {
  searchKeyword.value = ''
}
</script>

<style scoped>
.header-container {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 36px;
  height: 82px;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  color: inherit;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #22d3ee, #4f46e5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  color: #fff;
  letter-spacing: 1px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.brand-slogan {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(100, 116, 139, 0.88);
}

.nav-menu {
  flex: 1;
  border: none;
  background-color: transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-menu :deep(.el-menu-item) {
  border-radius: 12px;
  padding: 0 18px;
  height: 42px;
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #475569;
  transition: all 0.2s ease;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(79, 70, 229, 0.16);
  color: #4338ca;
}

.nav-menu :deep(.el-menu-item:not(.is-active):hover) {
  background: rgba(226, 232, 240, 0.6);
  color: #0f172a;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.global-search {
  width: 280px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
}

.search-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-title {
  font-size: 14px;
  color: #0f172a;
  font-weight: 600;
}

.option-meta {
  font-size: 12px;
  color: #64748b;
}

@media (max-width: 960px) {
  .global-search {
    display: none;
  }
}

.user-name {
  color: #0f172a;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.user-meta span {
  font-size: 12px;
  color: rgba(100, 116, 139, 0.8);
}

.ghost-btn {
  border-color: rgba(15, 23, 42, 0.18);
  color: #1e293b;
  background-color: rgba(248, 250, 252, 0.92);
}

.ghost-btn:hover {
  border-color: #4338ca;
  color: #4338ca;
  background-color: rgba(226, 232, 240, 0.6);
}
</style>
