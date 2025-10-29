import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_superuser || false)
  
  function setToken(newToken, newRefreshToken = null) {
    token.value = newToken
    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      refreshToken.value = newRefreshToken
      localStorage.setItem('refreshToken', newRefreshToken)
    }
  }
  
  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }
  
  async function login(credentials) {
    try {
      const response = await axios.post('/api/users/auth/login/', credentials)
      const { access, refresh, user } = response.data
      
      setToken(access, refresh)
      setUserInfo(user)
      
      // 设置 axios 默认 header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || '登录失败')
    }
  }
  
  async function register(userData) {
    try {
      const response = await axios.post('/api/users/auth/register/', userData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.username?.[0] 
        || error.response?.data?.email?.[0]
        || error.response?.data?.detail 
        || '注册失败'
      throw new Error(message)
    }
  }
  
  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
    delete axios.defaults.headers.common['Authorization']
  }
  
  // 初始化时设置 token
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }
  
  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    isAdmin,
    setToken,
    setUserInfo,
    login,
    register,
    logout,
  }
})
