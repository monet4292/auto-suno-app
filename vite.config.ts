import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Base configuration for Electron
  base: './',

  // Build configuration
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },

  // Development server configuration
  server: {
    port: 5173,
    strictPort: false, // Auto-find next available port if 5173 is taken
    hmr: {
      port: 5173
    },
    // Allow external connections for Electron
    host: 'localhost'
  },

  // Dependency optimization
  optimizeDeps: {
    exclude: ['electron']
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'frontend/components'),
      '@/hooks': resolve(__dirname, 'frontend/hooks'),
      '@/utils': resolve(__dirname, 'frontend/utils'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/electron': resolve(__dirname, 'electron')
    }
  },

  // Global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '3.0.0'),
    __PLATFORM__: JSON.stringify(process.platform)
  },

  // CSS configuration
  css: {
    devSourcemap: true
  }
});