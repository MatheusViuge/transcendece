#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT"

info() {
  printf '\n==> %s\n' "$1"
}

info "Checking Design System foundations"
test -f frontend/src/design-system/tokens.ts
test -f frontend/src/design-system/icons.tsx
grep -q -- '--color-primary:' frontend/src/assets/index.css
grep -q -- '--color-success:' frontend/src/assets/index.css
grep -q -- '--font-sans:' frontend/src/assets/index.css

info "Checking 10+ reusable components"
component_count=$(grep -c 'component:' frontend/src/design-system/inventory.ts)
if [ "$component_count" -lt 10 ]; then
  echo "Expected at least 10 Design System components, found $component_count" >&2
  exit 1
fi
printf 'Documented components: %s\n' "$component_count"

info "Checking decoupled brand assets"
test -f frontend/src/brand/assets.ts
test -f frontend/src/brand/identity.ts
test -f frontend/src/brand/BrandLogo.tsx

direct_imports=$(
  grep -RE '@/assets/(logo_|simbolo_|fotoheader)' frontend/src --include='*.ts' --include='*.tsx' \
    | grep -v '^frontend/src/brand/assets.ts:' || true
)
if [ -n "$direct_imports" ]; then
  printf 'Brand assets imported outside brand facade:\n%s\n' "$direct_imports" >&2
  exit 1
fi

info "Checking evaluation gallery route"
grep -q 'path="/design-system"' frontend/src/routes/AppRoutes.tsx
test -f frontend/src/pages/Publico/DesignSystem.tsx

info "Design System structural check passed."
