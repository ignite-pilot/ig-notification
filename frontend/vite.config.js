import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Phase별 설정 (환경 변수 또는 기본값: local)
const phase = process.env.PHASE || 'local'

// Phase별 포트 설정
const portConfig = {
  local: {
    port: 8100,
    apiPort: 8101
  },
  alpha: {
    port: 8100,
    apiPort: 8101
  }
}

const config = portConfig[phase] || portConfig.local

export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.FRONTEND_PORT || config.port),
    proxy: {
      '/api': {
        target: phase === 'alpha' 
          ? `http://alpha.ig-notification.ig-pilot.com:${config.apiPort}`
          : `http://localhost:${config.apiPort}`,
        changeOrigin: true
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js'
  }
})
