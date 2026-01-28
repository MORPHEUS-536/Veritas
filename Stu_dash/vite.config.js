import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 1574,
    host: 'localhost',
    strictPort: true,
  },
})
