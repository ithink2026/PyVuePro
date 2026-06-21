import { defineConfig } from 'vite'
import uniPlugin from '@dcloudio/vite-plugin-uni'

// CJS 模块的 default export 需要通过 .default 访问
const uni = uniPlugin.default || uniPlugin

export default defineConfig({
  plugins: [uni()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  base: '/h5/',
})