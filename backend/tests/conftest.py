from __future__ import annotations

import re
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (register mappers)
from app.core import ratelimit
from app.core.deps import get_db
from app.db import Base
from app.main import app
from app.services import notification_service, otp_service

OTP_RE = re.compile(r"(\d{4,8})")


class _Outbox(list):
    async def send(self, *args) -> None:  # matches provider .send signatures
        self.append(args)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    ratelimit.reset()
    yield
    ratelimit.reset()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def sms_outbox(monkeypatch) -> _Outbox:
    box = _Outbox()
    monkeypatch.setattr(otp_service, "get_sms_provider", lambda: box)
    return box


@pytest.fixture
def email_outbox(monkeypatch) -> _Outbox:
    box = _Outbox()
    monkeypatch.setattr(notification_service, "get_email_provider", lambda: box)
    return box


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    async def _attach_csrf(request):
        token = transport_client.cookies.get("csrf_token")
        if token and request.method not in ("GET", "HEAD", "OPTIONS"):
            request.headers.setdefault("X-CSRF-Token", token)

    transport = ASGITransport(app=app)
    transport_client = AsyncClient(
        transport=transport,
        base_url="http://test",
        event_hooks={"request": [_attach_csrf]},
    )
    async with transport_client as c:
        yield c
    app.dependency_overrides.clear()


async def login(client: AsyncClient, sms_outbox: _Outbox, phone: str) -> dict:
    """Run the real OTP flow; leaves auth cookies on the client. Returns SessionOut."""
    r = await client.post("/auth/otp/request", json={"phone": phone})
    assert r.status_code == 200, r.text
    to, text = sms_outbox[-1]
    code = OTP_RE.search(text).group(1)
    r = await client.post("/auth/otp/verify", json={"phone": phone, "code": code})
    assert r.status_code == 200, r.text
    return r.json()


async def set_profile(client: AsyncClient, name: str, **fields) -> dict:
    r = await client.patch("/users/me", json={"display_name": name, **fields})
    assert r.status_code == 200, r.text
    return r.json()


async def as_user(client: AsyncClient, db_session, phone: str, name: str | None = None) -> int:
    """Create a user + session directly (no OTP) and put the cookies on the client."""
    from app.services.auth_service import get_or_create_user, issue_session
    from app.services.phone import normalize_phone

    user, _ = await get_or_create_user(db_session, normalize_phone(phone))
    if name and not user.display_name:
        user.display_name = name
        await db_session.commit()
    issued = await issue_session(db_session, user.id)
    client.cookies.set("access_token", issued.access_token)
    client.cookies.set("refresh_token", issued.refresh_token)
    client.cookies.set("csrf_token", issued.csrf_token)
    return user.id
