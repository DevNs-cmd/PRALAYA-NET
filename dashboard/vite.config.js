import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // Standard Vite output
    emptyOutDir: true
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => {
          console.log(`[Vite Proxy] Forwarding ${path} to http://127.0.0.1:8000${path}`);
          return path;
        },
        onError: (err) => {
          console.error('[Vite Proxy] Error:', err);
        }
      }
    }
  }
})
