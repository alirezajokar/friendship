# Friendship app

A friendship PWA: phone-OTP login, a reusable invite link, friend requests,
a gift wishlist with surprise-preserving "claim", and multi-window birthday
reminders. Two independent apps in one repo: `backend/` (FastAPI) and
`frontend/` (Vue 3), plus `openspec/` holding the behavior spec.

## Where to go

- Working only on the API/data/scheduling? Read `backend/AGENTS.md`.
- Working only on the UI/PWA? Read `frontend/AGENTS.md`.
- Touching both, or adding a new capability end-to-end? Read this file, then
  both of the above.

## Before you change anything

Read `openspec/project.md` (stack, conventions) and the relevant
`openspec/specs/<capability>/spec.md` (auth, profile, invites, friends,
wishlist, notifications, birthday-reminders) before implementing — that's
the source of truth for expected behavior, not this file. If behavior
changes, update the spec too (or run the OpenSpec change flow: `/opsx:propose`).

## Run & verify

```
docker compose up --build     # db + migrate + api + worker + web, zero manual setup
```
Backend: `cd backend && .venv/bin/ruff check . && .venv/bin/python -m pytest -q`
Frontend: `cd frontend && npm run lint && npm run test && npm run build`
CI (`.github/workflows/ci.yml`) runs exactly those four backend/frontend checks on every push/PR.

## Architecture you can't infer from the code

- **Birthdays are Jalali-first.** `birth_jyear/jmonth/jday` are the stored
  source of truth; the anniversary is resolved in the Jalali calendar every
  year (a fixed Jalali day maps to a *different* Gregorian date depending on
  Jalali leap years — reusing a stored Gregorian month/day would be wrong
  ~1 year in 4). See `openspec/specs/birthday-reminders/spec.md`.
- **Session model**: short access JWT (cookie) + rotating opaque refresh
  token; reusing an already-rotated refresh token revokes the whole session
  family. CSRF is a double-submit cookie, not a header secret.
- **Wishlist claims**: the owner's own view never carries claim info, at all;
  friends see only "reserved / free" on someone else's claim, never who
  claimed it. This is enforced in `wishlist_service`, never in a router.
- **No Redis/Celery, on purpose** — single-node target, so rate limiting is
  in-process and the birthday job is one hourly APScheduler tick in the
  `worker` container. Don't introduce a queue/broker without discussing it.
- **No file uploads / object storage, on purpose** — avatars and wishlist
  item images are URLs only.
- The `migrate` compose service runs `alembic upgrade head` automatically
  before `api`/`worker` start. Don't reintroduce a manual migration step in
  the docs or compose files.

## Security

- Every mutating request needs `X-CSRF-Token` matching the `csrf_token`
  cookie (enforced by `enforce_csrf`); a 403 there almost always means a
  missing/stale CSRF header, not a real auth bug.
- Secrets only via env (`.env`, never committed — see `.env.example` for the
  full list). OTP codes are only ever visible in the `console` SMS
  provider's logs in dev; never a real send target.
