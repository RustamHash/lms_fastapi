import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  /** Один URL бэкенда для dev; переопределение: `VITE_DEV_BACKEND` в `.env.development` */
  const devBackend = env.VITE_DEV_BACKEND ?? 'http://127.0.0.1:8080'

  const proxyPrefixes = ['/api', '/docs', '/openapi.json', '/redoc'] as const
  const proxy = Object.fromEntries(
    proxyPrefixes.map((prefix) => [
      prefix,
      { target: devBackend, changeOrigin: true as const },
    ]),
  )

  return {
    plugins: [react()],
    server: { proxy },
  }
})
