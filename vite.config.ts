import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: 'static',
    emptyOutDir: false,
    rollupOptions: {
      input: './static/css/input.css',
      output: {
        assetFileNames: (assetInfo) =>
          assetInfo.name === 'input.css' ? 'css/output.css' : 'assets/[name][extname]',
      },
    },
  },
})
