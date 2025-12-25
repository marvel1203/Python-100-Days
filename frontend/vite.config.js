import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
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
          target: env.VITE_API_TARGET || 'http://localhost:8020',
          changeOrigin: true,
        },
        '/course-res': {
          target: env.VITE_API_TARGET || 'http://localhost:8020',
          changeOrigin: true,
        },
      },
    },
  }
})
