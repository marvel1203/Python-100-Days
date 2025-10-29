import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 9540,
    proxy: {
      '/api': {
        target: 'http://backend:8020',  // 使用Docker容器名称
        changeOrigin: true,
      },
      '/course-res': {
        target: 'http://backend:8020',  // 课程资源文件代理到后端
        changeOrigin: true,
      },
    },
  },
})
