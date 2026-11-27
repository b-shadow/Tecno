import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Capa 1 (presentación). En la facultad: VITE_BASE=/inf513/grupo05sa/proyecto2/ npm run build
// En desarrollo, /api se reenvía a la API de Laravel (capa 2); en Docker, VITE_API_PROXY=http://app:8001.
export default defineConfig(({ mode }) => {
  const env = { ...process.env, ...loadEnv(mode, process.cwd(), '') }
  // changeOrigin: false conserva el Host del navegador, así las URL absolutas de Laravel (asset()) apuntan a Vite.
  const destino = { target: env.VITE_API_PROXY || 'http://127.0.0.1:8001', changeOrigin: false }
  const proxy = { '/api': destino, '/catalogo-demo': destino }
  return {
    base: env.VITE_BASE || '/',
    plugins: [react(), tailwindcss()],
    // Garantiza una única instancia de React/ReactDOM y precompila dependencias de rutas diferidas (chart.js)
    // desde el arranque para evitar regeneraciones de browserHash y desfases `?v=` entre módulos ESM en desarrollo.
    resolve: {
      dedupe: ['react', 'react-dom', 'react-router-dom'],
    },
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-dom/client',
        'react/jsx-runtime',
        'react/jsx-dev-runtime',
        'react-router-dom',
        'axios',
        'lucide-react',
        'chart.js',
      ],
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      // En Docker sobre Windows no llegan los eventos de archivos: VITE_POLLING=1 los revisa por sondeo.
      watch: env.VITE_POLLING ? { usePolling: true, interval: 300 } : undefined,
      proxy,
    },
    preview: { port: 4173, proxy },
  }
})
