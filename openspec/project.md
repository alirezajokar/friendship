# Project Context

## Purpose

A friendship PWA: people register with a phone number, share a reusable invite
link, accept/decline friend requests, keep a gift **wishlist** that friends can
"claim" without spoiling the surprise for the owner, and receive **birthday
reminders** for their friends.

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 (async) + Alembic, PostgreSQL,
  APScheduler (in a separate `worker` process), `persiantools` for Jalali dates,
  `pywebpush` for Web Push.
- **Frontend**: Vue 3 + Vite + TypeScript, PrimeVue (Aura), Pinia, vue-router,
  vue-i18n (fa default, RTL), `vite-plugin-pwa` (injectManifest), `jalaali-js`.
- **Infra**: Docker Compose (`db`, `api`, `worker`, `web`). No reverse proxy in
  the repo — TLS is terminated in front of the stack.

## Project Conventions

### Structure

- `backend/app/api` (routers) → `app/services` (business logic) → `app/models`
  (SQLAlchemy) → `app/providers` (pluggable SMS / email / push).
- Routers stay thin; all rules live in services. Visibility/permission checks are
  never done in a router.
- `frontend/src/views` are route components; `src/api` wraps every endpoint;
  `src/stores` holds cross-view state (auth, notifications).

### Code Style

- Backend: `ruff` (line length 100, rules E/F/I/UP/B/C4). Async everywhere.
  Domain errors raise `AppError(status, "snake_case_code")`; the frontend maps
  codes to localized messages.
- Frontend: `eslint` flat config; formatting-only vue rules disabled (no
  formatter in the repo). Prefer Composition API `<script setup lang="ts">`.

### Architecture

- **Auth**: phone OTP only. Access JWT (30 min) + rotating opaque refresh token
  (30-day sliding, 90-day absolute cap), both `HttpOnly; Secure; SameSite=Lax`
  cookies. Refresh-token reuse revokes the whole session family. CSRF via a
  double-submit `csrf_token` cookie + `X-CSRF-Token` header on mutations.
- **Dates**: a user's birthday is stored as its **Jalali** (year optional,
  month, day) components — the source of truth. Anniversaries are resolved in
  the Jalali calendar every year (30-Esfand falls back to 29-Esfand in common
  years). `persiantools` on the backend is the single conversion authority.
- **Background work**: the `worker` process runs one hourly APScheduler job
  (`app.services.birthday_service.run_scan`). No Redis/Celery.

### Testing

- Backend: `pytest` + `httpx.AsyncClient`, in-memory SQLite. `ruff check` must pass.
- Frontend: `vitest`; `vue-tsc --noEmit` (via `npm run build`) must pass.

## Important Constraints

- Single-node deployment; the rate limiter is in-process.
- No file uploads / object storage — avatars and item images are URLs only.
- Google login is intentionally out of scope for v1 (seam left in `auth_service`).

## External Dependencies

- SMS provider (default `console`; `kavenegar` skeleton present).
- Email provider (default `console`; `smtp` implemented).
- Web Push needs a VAPID keypair (`VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY`).
