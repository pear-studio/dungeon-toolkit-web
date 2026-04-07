import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      react(),
      tailwindcss(),
    ],
    server: {
      port: 5173,
      host: '0.0.0.0',
      hmr: {
        // 解决 WSL2 + Docker 环境下 WebSocket 连接失败的问题
        host: 'localhost',
        clientPort: 5173,
        protocol: 'ws',
      },
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
        '/ws': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          ws: true,
        },
      },
      // Docker + Windows 挂载目录下必须使用轮询（inotify 不工作）
      watch: {
        usePolling: true,
        interval: 100,
      },
    },
  }
})