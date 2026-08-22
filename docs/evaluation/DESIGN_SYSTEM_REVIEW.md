# Design System review checklist

## Foundations
- [ ] `/design-system` shows semantic palette and typography.
- [ ] primary/success/warning/danger states are distinguishable and legible.
- [ ] focus indicators remain visible with keyboard navigation.

## Components
- [ ] inventory contains at least 10 owned reusable components.
- [ ] Button primary/accent/secondary/danger/ghost states render.
- [ ] Button loading and disabled states are understandable.
- [ ] Input, Select and Textarea have associated labels and visible focus.
- [ ] Alert semantics are understandable without relying only on color.
- [ ] Modal exposes dialog semantics and closes with Escape.
- [ ] Pagination buttons expose accessible names.
- [ ] 404 and construction pages use `EmptyState`.

## Identity swap architecture
- [ ] no product component imports `logo_*`, `simbolo_*` or `fotoheader` directly.
- [ ] brand physical files are mapped only in `brand/assets.ts`.
- [ ] brand copy is centralized in `brand/identity.ts` where applicable.
- [ ] Navbar/Footer/Hero render through the brand facade.

## Regression
- [ ] `cd frontend && npm ci && npm run lint && npm run build` passes.
- [ ] `sh scripts/design-system-check.sh` passes.
- [ ] HTTPS deployment can refresh `/design-system` directly.
- [ ] existing public/auth screens remain usable.

A reviewer should only approve Epic #23 after the CI is green and the visual/keyboard spot-check above is satisfactory.
