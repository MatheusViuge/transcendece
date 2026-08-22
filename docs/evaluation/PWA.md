# Progressive Web App — evaluation evidence

This document supports Epic #24 and child issues #42–#45.

## What is implemented

### Installability

- the production build emits `manifest.webmanifest` through a custom Vite plugin;
- manifest metadata comes from the centralized brand identity instead of duplicating the product name in an unrelated static JSON file;
- `brand/pwa.ts` centralizes PWA colors and icon paths;
- 192x192 and 512x512 PNG application icons are available under `/pwa/`;
- the manifest declares `/` as both `start_url` and `scope` and uses `display: standalone`;
- HTTPS is already provided by the project reverse proxy.

### Service Worker

`public/sw.js` implements two versioned caches:

- shell cache for `/`, the manifest, offline fallback and brand/PWA assets;
- runtime asset cache for same-origin scripts, styles, images and fonts.

Safety rules are intentionally conservative:

- requests other than GET bypass the cache;
- every `/api/` request bypasses the cache;
- cross-origin requests bypass the cache;
- no background mutation queue or fake offline synchronization exists;
- old caches belonging to this PWA are removed on activation;
- `sw.js` is served with `no-cache, no-store, must-revalidate` so browser update checks are not blocked by Nginx caching.

### Offline UX

The React application observes browser online/offline events. While offline it shows a global warning explaining that previously loaded content may remain available but server-dependent actions require connectivity and are not simulated locally.

For navigation failures, the Service Worker prefers the cached SPA shell and falls back to `offline.html` if the application shell is unavailable.

## Automated evidence

Run after a production build:

```bash
cd frontend
npm ci
npm run lint
npm run build
cd ..
sh scripts/pwa-check.sh
```

The check verifies:

- required manifest fields;
- exact 192x192 and 512x512 PNG dimensions;
- Service Worker registration;
- cache versioning and cleanup;
- explicit bypass of non-GET and `/api/` traffic;
- offline fallback;
- Nginx anti-cache policy for `sw.js`;
- presence of the global offline UX.

The GitHub deployment job also verifies the manifest, Service Worker, offline fallback and icons through the real HTTPS reverse proxy.

## Chrome evaluation demo

1. Start a clean production deployment with `docker compose up --build`.
2. Open `https://localhost` in the current stable Chrome and accept the local certificate warning if needed.
3. In DevTools → Application → Manifest, confirm name, standalone display and 192/512 icons without manifest errors.
4. In Application → Service Workers, confirm `/sw.js` is activated and controls the page.
5. Install the application from Chrome's install UI and launch it in standalone mode.
6. Browse the home/catalog once so application assets are available to the runtime cache.
7. In DevTools Network, switch to Offline and reload.
8. Confirm the application shell still opens and the offline warning is visible.
9. Try an action that needs the backend and confirm the UI does not claim that the mutation was saved/synchronized.
10. Switch back Online; confirm the warning disappears without a destructive reload and normal server-backed flows work again.
11. After a later deployment with a changed `CACHE_VERSION`, confirm the previous `consuelo-pwa-*` caches are removed during Service Worker activation.

## Brand replacement note

A future visual-identity replacement remains localized. Product metadata comes from `src/brand/identity.ts`, PWA colors/paths from `src/brand/pwa.ts`, and install icons from `public/pwa/`. Replacing the brand does not require editing product pages or the Service Worker cache policy.
