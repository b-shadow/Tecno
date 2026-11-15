import { defineConfig } from 'vite'
import laravel from 'laravel-vite-plugin'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // En el servidor de la facultad: CRM_ASSET_BASE=/inf513/grupo05sa/proyecto2/build/ npm run build
  base: process.env.CRM_ASSET_BASE || '/build/',
  plugins: [
    laravel({
      input: 'resources/js/app.js',
      refresh: true,
    }),
    vue({
      template: {
        transformAssetUrls: {
          base: null,
          includeAbsolute: false,
        },
      },
    }),
  ],
  server: {
    // Escucha en todas las interfaces para correr dentro de Docker; el navegador entra por localhost.
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    origin: 'http://localhost:5173',
    cors: true,
  },
})
