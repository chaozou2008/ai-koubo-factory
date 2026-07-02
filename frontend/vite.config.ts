import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    allowedHosts: [".serveousercontent.com", ".serveo.net", ".lhr.life", ".loca.lt", "localhost"],
    hmr: false,
  },
  preview: {
    allowedHosts: [".serveousercontent.com", ".serveo.net", ".lhr.life", ".loca.lt", "localhost"],
  },
})
