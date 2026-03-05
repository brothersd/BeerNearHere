// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  server: {
    host: '0.0.0.0',  // Allow external connections (required for Docker)
    port: 5173,        // Vite default port
    strictPort: true,  // Fail if port is already in use
    
    // Proxy API requests to Django backend
    proxy: {
      '/api': {
        target: 'http://web:8000',  // Docker service name, not localhost
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,  // Helpful for debugging
  },
  
  // Resolve React fast refresh
  // esbuild: {
  //   jsx: 'automatic',
  // },
})