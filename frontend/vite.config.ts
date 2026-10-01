import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In Docker Compose the backend is reachable as http://backend:8000.
const apiTarget = process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': apiTarget,
    },
  },
})
