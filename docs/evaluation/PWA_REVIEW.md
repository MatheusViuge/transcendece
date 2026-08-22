# PWA review checklist

Parent Epic: #24

## Automated

- [ ] `npm run lint` passes
- [ ] `npm run build` passes
- [ ] `sh scripts/pwa-check.sh` passes
- [ ] Mandatory backend regression remains green
- [ ] Docker images build in the serial backend → frontend → proxy order
- [ ] `/manifest.webmanifest` is served through HTTPS
- [ ] `/sw.js` is served through HTTPS with no-store/no-cache semantics
- [ ] `/offline.html` and both PWA icons are served through HTTPS
- [ ] Framework/ORM and Design System regression checks remain green

## Chrome manual review

- [ ] Manifest has no blocking errors in DevTools
- [ ] 192x192 and 512x512 icons render correctly
- [ ] Service Worker is activated and controls the application
- [ ] Chrome offers/permits installation
- [ ] Installed app opens in standalone mode
- [ ] Previously loaded application shell works after switching DevTools to Offline
- [ ] Offline warning is visible and understandable
- [ ] API/private responses are not present in Cache Storage
- [ ] Mutations are not falsely reported as synchronized while offline
- [ ] Online → offline → online transition recovers without destructive reload
- [ ] Updating the Service Worker removes old PWA cache versions
- [ ] Console has no relevant application errors/warnings

## Module gate

- [ ] #42 validated
- [ ] #43 validated
- [ ] #44 validated
- [ ] #45 evidence recorded
- [ ] Epic #24 ready to merge/close
