import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { brandIdentity } from './src/brand/identity'
import { brandPwa } from './src/brand/pwa'

const manifest = {
  name: brandIdentity.name,
  short_name: brandIdentity.shortName,
  description: brandIdentity.description,
  lang: 'pt-BR',
  start_url: brandPwa.startUrl,
  scope: brandPwa.scope,
  display: brandPwa.display,
  theme_color: brandPwa.themeColor,
  background_color: brandPwa.backgroundColor,
  prefer_related_applications: false,
  icons: [
    {
      src: brandPwa.icons.small,
      sizes: '192x192',
      type: 'image/png',
      purpose: 'any maskable',
    },
    {
      src: brandPwa.icons.large,
      sizes: '512x512',
      type: 'image/png',
      purpose: 'any maskable',
    },
  ],
}

const manifestSource = `${JSON.stringify(manifest, null, 2)}\n`

function brandedPwaManifest(): Plugin {
  return {
    name: 'branded-pwa-manifest',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const pathname = request.url?.split('?')[0]
        if (pathname !== '/manifest.webmanifest') return next()

        response.statusCode = 200
        response.setHeader('Content-Type', 'application/manifest+json; charset=utf-8')
        response.setHeader('Cache-Control', 'no-cache')
        response.end(manifestSource)
      })
    },
    generateBundle() {
      this.emitFile({
        type: 'asset',
        fileName: 'manifest.webmanifest',
        source: manifestSource,
      })
    },
    transformIndexHtml(html) {
      return {
        html: html.replace('__BRAND_NAME__', brandIdentity.name),
        tags: [
          {
            tag: 'link',
            attrs: { rel: 'manifest', href: '/manifest.webmanifest' },
            injectTo: 'head',
          },
          {
            tag: 'meta',
            attrs: { name: 'theme-color', content: brandPwa.themeColor },
            injectTo: 'head',
          },
          {
            tag: 'meta',
            attrs: { name: 'application-name', content: brandIdentity.name },
            injectTo: 'head',
          },
          {
            tag: 'meta',
            attrs: { name: 'apple-mobile-web-app-capable', content: 'yes' },
            injectTo: 'head',
          },
          {
            tag: 'link',
            attrs: { rel: 'apple-touch-icon', href: brandPwa.icons.small },
            injectTo: 'head',
          },
        ],
      }
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    brandedPwaManifest(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
