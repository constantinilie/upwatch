import { fileURLToPath, URL } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // In development /api/* is proxied to Django, so the frontend and the API share one origin (no CORS).
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
