import { fileURLToPath, URL } from 'node:url'
import { copyFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    {
      name: 'create-no-daily-html',
      closeBundle() {
        const distDir = resolve(import.meta.dirname, 'dist')
        const noDailyDir = resolve(distDir, 'no-daily')

        mkdirSync(noDailyDir, { recursive: true })
        copyFileSync(resolve(distDir, 'index.html'), resolve(noDailyDir, 'index.html'))
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
