import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      // Special handling for auth endpoints
      '/api/auth': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('[Auth Proxy Error]', err);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log(`[Auth Proxy] ${req.method} ${req.url} -> ${proxyRes.statusCode}`);
            // Log redirect headers for auth callbacks
            if (proxyRes.headers.location) {
              console.log(`[Auth Redirect] -> ${proxyRes.headers.location}`);
            }
          });
        }
      },
      // General API proxy for other endpoints
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
        // Handle login callback redirects
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('[Proxy Error]', err);
          });
          // Log responses for debugging
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log(`[Proxy] ${req.method} ${req.url} -> ${proxyRes.statusCode}`);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log(`[Proxy Request] ${req.method} ${req.url}`);
          });
        }
      }
    },
    // Handle CORS for all local development
    cors: true,
    // Log environment variables at server start (excluding secrets)
    onBeforeStart: () => {
      console.log('Starting Vite development server with:');
      console.log('- Environment: ', process.env.NODE_ENV);
      console.log('- API Base URL: ', process.env.VITE_API_BASE_URL || 'Not defined (will use proxy)');
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: true
  }
});