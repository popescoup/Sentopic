import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // THIS IS THE KEY FIX - generates relative paths for Electron
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy API requests to your FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,  // 🔒 SECURITY: Remove source maps from production build
    minify: 'terser',  // 🔒 SECURITY: Enhanced minification  
    terserOptions: {
      compress: {
        drop_console: true,    // Remove console.log statements from production
        drop_debugger: true,   // Remove debugger statements
        passes: 2              // Multiple compression passes for better minification
      },
      mangle: {
        toplevel: true         // Rename top-level variables for better obfuscation
      }
    }
  },
})