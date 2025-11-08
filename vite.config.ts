import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        // SECURE: Proxy URL instead of API key
        'process.env.GEMINI_PROXY_URL': JSON.stringify(env.GEMINI_PROXY_URL || 'https://gemini-proxy-YOUR-ID.run.app'),
        // Fallback for local development (uses .env file)
        'process.env.GEMINI_API_KEY': env.NODE_ENV === 'development' ? JSON.stringify(env.GEMINI_API_KEY) : 'undefined'
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
