import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// Load environment variables
const env = loadEnv(process.env.MODE || 'development', process.cwd())

export default defineConfig({
  plugins: [react()],
  define: {
    __APP_ENV__: JSON.stringify(env.MODE || 'development'),
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: false
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': {
        target: env.VITE_API_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => {
          console.log(`[Vite Proxy] Forwarding ${path} to ${env.VITE_API_URL || 'http://127.0.0.1:8000'}${path}`)
          return path
        },
        onError: (err) => {
          console.error('[Vite Proxy] Error:', err)
        }
      },
      '/ws': {
        target: (env.VITE_WS_URL || 'ws://127.0.0.1:8000').replace(/^http/, 'ws'),
        changeOrigin: true,
        secure: false,
        ws: true
      }
    }
  }
})

