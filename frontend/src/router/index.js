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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - Python-100天从新手到大师`
  
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
