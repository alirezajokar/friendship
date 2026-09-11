# اپ دوستی (Friendship)

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

وب‌اپ دوستی (PWA): ورود با شماره موبایل، لینک دعوت، ویش‌لیست هدیه با قابلیت
«رزرو» بدون لو رفتن سورپرایز، و یادآور چندمرحله‌ای تولد دوستان.

- **بک‌اند**: FastAPI + SQLAlchemy async + Alembic + PostgreSQL + APScheduler
- **فرانت‌اند**: Vue 3 + Vite + TypeScript + PrimeVue + PWA (فارسی، RTL)
- **جریان کار**: [OpenSpec](https://github.com/Fission-AI/OpenSpec) — `openspec/`

---

## اجرا با Docker (پیشنهادی)

فقط همین یک دستور — بدون هیچ تنظیم اولیه‌ای:

```bash
docker compose up --build
```

سرویس `migrate` قبل از `api`/`worker` به‌صورت خودکار `alembic upgrade head` را
اجرا می‌کند، پس نیازی به مهاجرت دستی نیست. فایل `.env` هم اختیاری است (مقادیر
پیش‌فرض توسعه در `docker-compose.yml` جاسازی شده‌اند)؛ برای سفارشی‌سازی:
`cp .env.example .env`.

- API: <http://localhost:8000> (مستندات تعاملی: `/docs`)
- وب: <http://localhost:5173>
- **کد ورود (OTP)** در حالت توسعه پیامک نمی‌شود؛ در لاگ سرویس `api` چاپ می‌شود:
  ```bash
  docker compose logs -f api | grep SMS
  # خروجی نمونه:  SMS -> +989121234567 | کد ورود شما به اپ دوستی: 944481
  ```

### توقف و پاک‌سازی

```bash
docker compose down           # توقف
docker compose down -v        # توقف + حذف دیتابیس (شروع تمیز)
```

### اگر خطای ۵۰۰ گرفتید

- **`relation ... does not exist`**: مهاجرت اجرا نشده. با نسخهٔ فعلی نباید رخ دهد؛
  اگر از تصویر قدیمی‌تر استفاده می‌کنید: `docker compose run --rm migrate` یا
  `docker compose exec api alembic upgrade head`.
- **خطای اتصال به دیتابیس**: چند ثانیه صبر کنید (کانتینر `db` هنوز healthy نشده) یا
  `docker compose restart api`.
- جزئیات خطا همیشه در `docker compose logs api` است.

### محیط production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

بدون reverse proxy/TLS است؛ آن را جلوی این استک قرار دهید و پورت‌های `api` (۸۰۰۰)
و `web` (۸۰۸۰) را ترمینیت کنید.

---

## اجرای محلی بدون Docker

### بک‌اند

```bash
cd backend
uv venv --python 3.12 && uv pip install -r pyproject.toml
uv pip install pytest pytest-asyncio ruff aiosqlite     # ابزار توسعه
export DATABASE_URL="postgresql+asyncpg://friendship:friendship@localhost:5432/friendship"
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
# worker (زمان‌بندی یادآورها) در ترمینال جدا:
.venv/bin/python -m app.worker
```

تست و لینت:

```bash
.venv/bin/ruff check .
.venv/bin/pytest -q
```

### فرانت‌اند

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
npm run lint && npm run test && npm run build
```

---

## Web Push (اختیاری)

یک‌بار کلید VAPID بسازید و در env قرار دهید:

```bash
cd backend && .venv/bin/python -m app.scripts.gen_vapid
```

- `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` → `.env` بک‌اند
- همان `VAPID_PUBLIC_KEY` → `VITE_VAPID_PUBLIC_KEY` فرانت‌اند

بدون این کلیدها، اعلان‌های in-app و ایمیل کار می‌کنند و Web Push غیرفعال می‌ماند.

---

## پیامک و ایمیل

پرووایدرها قابل‌تعویض‌اند (`app/providers/`):

| متغیر | پیش‌فرض | گزینه‌ها |
|---|---|---|
| `SMS_PROVIDER` | `console` (چاپ در لاگ) | `kavenegar` (اسکلت — کلید API لازم) |
| `EMAIL_PROVIDER` | `console` | `smtp` (نیازمند `SMTP_*`) |

افزودن پرووایدر جدید: کلاسی با متد `async send(...)` بسازید و در `registry.py` ثبت کنید.

---

## یادآور تولد

تاریخ تولد به‌صورت اجزای **شمسی** ذخیره می‌شود (سال اختیاری) و سالگرد هر سال در
تقویم شمسی حساب می‌شود تا با سال‌های کبیسه جابه‌جا نشود. آزمایش دستی:

```bash
docker compose exec worker python -m app.worker --run-now
docker compose exec worker python -m app.worker --run-now --base-now 2026-07-02T09:05:00+03:30
```

پنجره‌ها: پیش‌فرض ۷، ۳، ۱ (۲۱:۰۰) و ۰ (۰۹:۰۰) روز قبل — از `REMINDER_OFFSETS` قابل تنظیم.

---

## ساختار

```
backend/    FastAPI؛ app/api → app/services → app/models، app/providers، app/worker.py
frontend/   Vue 3؛ src/views، src/api، src/stores، src/sw.ts
openspec/   project.md + specs/<capability>/spec.md
docker-compose.yml / docker-compose.prod.yml
```

جزئیات رفتار در `openspec/specs/` و طرح اولیه در `openspec/project.md`.

---

## لایسنس

[MIT](LICENSE) — استفاده، تغییر و توزیع آزاد است، حتی به‌صورت تجاری/closed-source؛
کافی‌ست اعلامیهٔ کپی‌رایت حفظ شود. نرم‌افزار «همان‌طور که هست» و بدون ضمانت ارائه می‌شود.
