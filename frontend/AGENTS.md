# frontend (Vue 3)

Root `AGENTS.md` already covers the project-wide rules. This file only adds
what's specific to this app.

## Conventions

- Composition API only, `<script setup lang="ts">` — no Options API.
- Pinia (`src/stores/`) holds only cross-view state (`auth`, `notifications`
  currently). Anything scoped to one view stays local `ref`/`reactive` in
  that view.
- Never call `axios` directly from a component/view. Every request goes
  through `src/api/endpoints.ts`, which uses the shared `src/api/client.ts`
  instance — that's what attaches the CSRF header and silently retries once
  through `/auth/refresh` on a 401. A hand-rolled `fetch` bypasses both.

## Where new code goes

- New page → `src/views/<Name>View.vue` + a route in `src/router/index.ts`
  with the right `meta` (`requiresAuth`, and `allowIncompleteProfile` only
  for the profile-setup route itself).
- New UI string → add the key to `src/i18n/fa.json` first (it's the
  canonical/default locale), mirror it in `en.json`.
- New backend call → add a typed function to `src/api/endpoints.ts`, not
  inline in the component that uses it.

## Run & test

```
npm install
npm run dev      # vite dev server on :5173
npm run lint
npm run test     # vitest
npm run build    # vue-tsc --noEmit && vite build
```

## PWA

Service worker logic lives only in `src/sw.ts` (the `injectManifest`
strategy in `vite.config.ts` — precache + `push`/`notificationclick`
handlers). Don't add a second `registerSW`/service-worker registration
elsewhere.

## Gotchas

- ESLint's formatting-only Vue rules (attribute-per-line,
  self-closing-void-elements, attribute-hyphenation, etc.) are deliberately
  turned off in `eslint.config.js` — there's no Prettier in this repo. Don't
  "fix" those as lint warnings; they're not enabled on purpose.
- `jalaali-js` ships no types; `src/types/jalaali-js.d.ts` hand-declares the
  module. Extend that file rather than adding `@ts-ignore` at call sites.
