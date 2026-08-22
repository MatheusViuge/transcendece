# Custom-made Design System — evaluation evidence

This document is the technical evidence for Epic #23 and Issues #38–#41.

## Module claim

- Type: Minor
- Value: 1 point
- Cumulative roadmap value after Framework + ORM: 4/19
- UI framework/component library: none. Components are implemented in this repository using React, Tailwind CSS and `tailwind-variants` as a styling/variant helper.
- Icon source: React Icons, normalized behind the project's own `Icon` contract.

## Foundations

The semantic foundations live in `frontend/src/assets/index.css` and the inspectable token catalog lives in `frontend/src/design-system/tokens.ts`.

### Palette

Primary, success, warning, danger, surface, border and text colors are semantic tokens. Existing physical color aliases remain temporarily for backwards compatibility, but new Design System primitives consume semantic names.

### Typography

The application standardizes on Arimo with reusable body/small/heading scales. The root font stack is exposed as `--font-sans`.

### Shape and elevation

`control`, `card` and `pill` radius tokens plus card/dialog shadow tokens are centralized in the Tailwind theme.

### Focus and interaction

A global `:focus-visible` rule provides a visible keyboard outline. Form controls and custom components add consistent hover, focus, disabled and loading states.

## Icon system

`frontend/src/design-system/icons.tsx` is the only Design System icon contract. It defines a small canonical Lucide set, standard sizes and decorative/accessibility behavior. Consumers request an icon by semantic name instead of importing arbitrary icon families and dimensions.

## Reusable component inventory

The machine-readable inventory is `frontend/src/design-system/inventory.ts`. It currently documents 15 owned reusable components, including:

1. Button
2. Input
3. Select
4. Textarea
5. FormField
6. Card
7. Table
8. Badge
9. Alert
10. Spinner
11. EmptyState
12. Modal
13. Pagination
14. Icon
15. BrandLogo

The evaluation gallery at `/design-system` exercises the principal variants/states. Existing product screens continue to use Button/Form/Card/Table components; `EmptyState` is also used by 404/construction screens, `Badge` is used by password-strength feedback, and `Alert` is used by registration success feedback.

## Decoupled visual identity

Brand-specific files are deliberately isolated from application components:

- `frontend/src/brand/assets.ts` — maps physical logo/symbol/hero files to semantic asset slots;
- `frontend/src/brand/identity.ts` — brand name, description, copyright and hero copy;
- `frontend/src/brand/BrandLogo.tsx` — chooses wordmark/symbol and light/dark surface variant;
- `frontend/src/brand/index.ts` — public facade.

Navbar, Footer, Hero, auth headers and Loader consume this facade and do not import logo/symbol/hero files directly.

### Rebranding procedure

To change the visual identity without rewriting screens:

1. add/replace the desired physical logo, symbol and hero image files under `frontend/src/assets/`;
2. point `frontend/src/brand/assets.ts` at those files;
3. update names/copy in `frontend/src/brand/identity.ts`;
4. update semantic color/typography tokens in `frontend/src/assets/index.css` and `design-system/tokens.ts`;
5. run `npm run lint`, `npm run build` and `sh scripts/design-system-check.sh`.

No Navbar/Footer/Hero/auth component should need a brand-specific import change.

## Automated validation

`sh scripts/design-system-check.sh` fails when:

- semantic foundations disappear;
- the inventory falls below 10 components;
- a brand image is imported outside the brand facade;
- the `/design-system` evaluation route disappears.

The normal frontend lint/build remains authoritative for TypeScript and Tailwind compilation. The deployment workflow also requests `/design-system` through HTTPS to validate SPA routing in the containerized stack.

## Evaluation demo

1. Open `/design-system`.
2. Show the light/dark brand variants and explain the `brand/` facade.
3. Show palette and typography token sections.
4. Show Button variants, disabled/loading and keyboard focus.
5. Tab through Input/Select/Textarea and pagination controls.
6. Show Badge and Alert semantic states.
7. Open the Modal; close it with Escape.
8. Point to the inventory count (15 components).
9. Open `design-system/inventory.ts`, `icons.tsx`, `tokens.ts` and `brand/assets.ts` if the evaluator asks for code evidence.

## Manual review still expected

Before final evaluation, execute the global browser/rehearsal issues for Chrome console cleanliness, mobile/desktop visual review and full keyboard traversal. Those final-project checks remain intentionally separate from this module's implementation evidence.
