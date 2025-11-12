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
        target: 'http://localhost:8020',  // 直接访问Django服务
        changeOrigin: true,
      },
      '/course-res': {
        target: 'http://localhost:8020',  // 课程资源文件代理到后端
        changeOrigin: true,
      },
    },
  },
})
