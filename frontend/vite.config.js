import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // allow external access
    allowedHosts: 'all', // allow ngrok domain
    proxy: {
      '/api': {
        target: 'https://dz-clothes00.vercel.app/',
        changeOrigin: true,
      }
    }
  },
})
