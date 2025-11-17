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
        target: process.env.VITE_API_TARGET || 'http://backend:8020',
        changeOrigin: true,
      },
      '/course-res': {
        target: process.env.VITE_API_TARGET || 'http://backend:8020',
        changeOrigin: true,
      },
    },
  },
})
