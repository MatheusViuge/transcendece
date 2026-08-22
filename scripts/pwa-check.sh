#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DIST_DIR=${1:-"$ROOT_DIR/frontend/dist"}
MANIFEST="$DIST_DIR/manifest.webmanifest"
SW="$DIST_DIR/sw.js"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

[ -f "$MANIFEST" ] || fail "manifest.webmanifest was not emitted by the production build"
[ -f "$SW" ] || fail "sw.js is missing from the production build"
[ -f "$DIST_DIR/offline.html" ] || fail "offline.html is missing from the production build"
[ -f "$DIST_DIR/pwa/icon-192.png" ] || fail "192x192 PWA icon is missing"
[ -f "$DIST_DIR/pwa/icon-512.png" ] || fail "512x512 PWA icon is missing"

node - "$MANIFEST" "$DIST_DIR/pwa/icon-192.png" "$DIST_DIR/pwa/icon-512.png" <<'NODE'
const fs = require('node:fs');
const [manifestPath, icon192Path, icon512Path] = process.argv.slice(2);
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

function assert(condition, message) {
  if (!condition) {
    console.error(`ERROR: ${message}`);
    process.exit(1);
  }
}

function pngDimensions(file) {
  const data = fs.readFileSync(file);
  const signature = data.subarray(0, 8).toString('hex');
  assert(signature === '89504e470d0a1a0a', `${file} is not a PNG`);
  return [data.readUInt32BE(16), data.readUInt32BE(20)];
}

assert(Boolean(manifest.name), 'manifest.name is required');
assert(Boolean(manifest.short_name), 'manifest.short_name is required');
assert(manifest.start_url === '/', 'manifest.start_url must be /');
assert(manifest.scope === '/', 'manifest.scope must be /');
assert(manifest.display === 'standalone', 'manifest.display must be standalone');
assert(manifest.prefer_related_applications === false, 'prefer_related_applications must be false');
assert(Boolean(manifest.theme_color), 'theme_color is required');
assert(Boolean(manifest.background_color), 'background_color is required');

const sizes = new Set((manifest.icons || []).map((icon) => icon.sizes));
assert(sizes.has('192x192'), 'manifest must expose a 192x192 icon');
assert(sizes.has('512x512'), 'manifest must expose a 512x512 icon');
assert(manifest.icons.every((icon) => icon.type === 'image/png'), 'PWA icons must be PNG');

const icon192 = pngDimensions(icon192Path);
const icon512 = pngDimensions(icon512Path);
assert(icon192[0] === 192 && icon192[1] === 192, 'small PWA icon must be exactly 192x192');
assert(icon512[0] === 512 && icon512[1] === 512, 'large PWA icon must be exactly 512x512');
NODE

grep -Fq 'request.method !== "GET"' "$SW" || fail "service worker must bypass non-GET requests"
grep -Fq 'url.pathname.startsWith("/api/")' "$SW" || fail "service worker must bypass /api/ responses"
grep -Fq 'CACHE_VERSION' "$SW" || fail "service worker cache version is missing"
grep -Fq 'caches.delete' "$SW" || fail "service worker old-cache cleanup is missing"
grep -Fq '/offline.html' "$SW" || fail "offline navigation fallback is missing"
grep -Fq 'navigator.serviceWorker.register("/sw.js"' "$ROOT_DIR/frontend/src/pwa/registerServiceWorker.ts" || fail "service worker registration is missing"
grep -Fq 'import.meta.env.DEV' "$ROOT_DIR/frontend/src/pwa/registerServiceWorker.ts" || fail "service worker should stay disabled during Vite development"
grep -Fq 'Cache-Control "no-cache, no-store, must-revalidate"' "$ROOT_DIR/frontend/nginx.conf" || fail "sw.js must not be served with a long-lived HTTP cache"
grep -Fq 'Você está offline' "$ROOT_DIR/frontend/src/pwa/ConnectivityBanner.tsx" || fail "offline connectivity UX is missing"

printf 'PWA structural/security checks passed.\n'
