import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/courses',
    name: 'CourseList',
    component: () => import('@/views/courses/CourseList.vue'),
    meta: { title: '课程列表' }
  },
  {
    path: '/courses/:slug',
    name: 'CourseDetail',
    component: () => import('@/views/courses/CourseDetail.vue'),
    meta: { title: '课程详情' }
  },
  {
    path: '/courses/:courseSlug/:lessonSlug',
    redirect: to => {
      return { name: 'LessonDetail', params: { slug: to.params.lessonSlug } }
    }
  },
  {
    path: '/lessons/:slug',
    name: 'LessonDetail',
    component: () => import('@/views/lessons/LessonDetail.vue'),
    meta: { title: '课时详情' }
  },
  {
    path: '/exercises',
    name: 'ExerciseList',
    component: () => import('@/views/exercises/ExerciseList.vue'),
    meta: { title: '练习题库' }
  },
  {
    path: '/exercises/:slug',
    name: 'ExerciseDetail',
    component: () => import('@/views/exercises/ExerciseDetail.vue'),
    meta: { title: '练习详情' }
  },
  {
    path: '/progress',
    name: 'Progress',
    component: () => import('@/views/user/Progress.vue'),
    meta: { title: '学习进度', requiresAuth: true }
  },
  {
    path: '/notes',
    name: 'Notes',
    component: () => import('@/views/user/Notes.vue'),
    meta: { title: '我的笔记', requiresAuth: true }
  },
  {
    path: '/settings/ai',
    name: 'AISettings',
    component: () => import('@/views/user/AISettings.vue'),
    meta: { title: 'AI助手配置', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/admin',
    name: 'Admin',
    redirect: '/admin/users',
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('@/views/admin/UserManagement.vue'),
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - Python-100天从新手到大师`
  
  const userStore = useUserStore()
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router
