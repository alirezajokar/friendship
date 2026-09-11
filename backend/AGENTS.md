# backend (FastAPI)

Root `AGENTS.md` already covers the project-wide rules (Jalali birthdays,
session model, wishlist visibility, no Redis/Celery). This file only adds
what's specific to this app.

## Layering / where new code goes

`app/api` (thin routers, no business logic) → `app/services` (all
permission/visibility rules live here, never in a router) → `app/models`
(SQLAlchemy) → `app/providers` (SMS/email/push, swappable via a
`registry.py` keyed on an env var — see `SMS_PROVIDER`/`EMAIL_PROVIDER` in
`.env.example`).

- New endpoint → `app/api/<domain>.py`, register the router in
  `app/api/__init__.py`.
- New table/column → `app/models/<domain>.py`, then
  `alembic revision --autogenerate -m "..."` and read the generated file
  before applying — `app/db.py`'s `UTCDateTime` type needs the custom
  `render_item` hook already in `alembic/env.py`; don't let autogenerate
  import `app.*` into a migration file.
- New pluggable integration (another SMS/email/push vendor) →
  `app/providers/<kind>/`, implement the `Protocol` in that kind's `base.py`,
  and add it to that kind's `registry.py`.

## Run & test

```
uv venv --python 3.12
uv pip install -r pyproject.toml
uv pip install pytest pytest-asyncio ruff aiosqlite   # dev-only group
.venv/bin/ruff check .
.venv/bin/python -m pytest -q
```
Migrations: `alembic upgrade head` (needs `DATABASE_URL`; the `migrate`
compose service does this automatically in Docker). Run one birthday scan
without waiting for the hourly tick: `python -m app.worker --run-now`.

## Testing conventions (`tests/conftest.py`)

- `db_session`: fresh in-memory SQLite per test (StaticPool), not Postgres —
  fast, but means Postgres-only behavior isn't exercised here.
- `client`: httpx `AsyncClient` over the app; a request hook auto-attaches
  `X-CSRF-Token` from the `csrf_token` cookie, so tests don't repeat that.
- `sms_outbox` / `email_outbox`: monkeypatch the provider registries to
  capture sent messages instead of a real provider — use these to pull an
  OTP code out in a login-flow test.
- `login()`: drives the real OTP request/verify flow. `as_user()`: bypasses
  OTP and issues a session directly for a given phone — use this for
  multi-user tests (e.g. the wishlist visibility matrix) where driving OTP
  for every user would be noise.

## Gotchas

- `app` is not an installed package; `pyproject.toml` sets
  `pythonpath = ["."]` in `[tool.pytest.ini_options]` so tests import it
  regardless of whether pytest runs via `python -m pytest` or the `pytest`
  console script (`uv run pytest` uses the latter and fails without this).
- `UTCDateTime` (in `app/db.py`) normalizes every datetime column to
  tz-aware UTC on read, including on SQLite (which stores naive) — don't
  swap it back for a plain `DateTime(timezone=True)`, tz-naive comparisons
  will break on SQLite tests.
- The birthday reminder idempotency key is
  `(recipient_id, birthday_user_id, occurrence_jyear, offset_key)` — the
  **Jalali** year of the occurrence, not the Gregorian year, so windows that
  straddle Nowruz don't double-fire or get skipped.
