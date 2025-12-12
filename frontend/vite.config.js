import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Phase별 설정 (환경 변수 또는 기본값: local)
const phase = process.env.PHASE || 'local'

// Phase별 포트 설정
// 통합 서버이므로 frontend와 backend가 같은 포트 사용
const portConfig = {
  local: {
    port: 8101,  // 통합 서버 포트
    apiPort: 8101
  },
  alpha: {
    port: 8101,
    apiPort: 8101
  }
}

const config = portConfig[phase] || portConfig.local

export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.FRONTEND_PORT || config.port),
    // 통합 서버이므로 proxy 불필요 (같은 서버에서 서빙)
    // 개발 모드에서도 FastAPI 서버를 통해 서빙하도록 변경
    proxy: {
      '/api': {
        target: phase === 'alpha' 
          ? `http://alpha.ig-notification.ig-pilot.com:${config.apiPort}`
          : `http://localhost:${config.apiPort}`,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // 빌드된 파일이 FastAPI에서 서빙되도록 설정
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js'
  }
})
