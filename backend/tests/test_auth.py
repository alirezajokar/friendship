import pytest

from app.core import ratelimit
from tests.conftest import OTP_RE, login

pytestmark = pytest.mark.asyncio


async def test_full_otp_login(client, sms_outbox):
    body = await login(client, sms_outbox, "09120000001")
    assert body["is_new"] is True
    assert body["profile_completed"] is False

    me = await client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["phone"] == "+989120000001"


async def test_second_login_is_not_new(client, sms_outbox):
    await login(client, sms_outbox, "09120000002")
    await client.post("/auth/logout")
    ratelimit.reset()  # simulate the resend cooldown having elapsed
    body = await login(client, sms_outbox, "09120000002")
    assert body["is_new"] is False


async def test_wrong_code_then_lockout(client, sms_outbox):
    await client.post("/auth/otp/request", json={"phone": "09120000003"})
    for _ in range(5):
        r = await client.post("/auth/otp/verify", json={"phone": "09120000003", "code": "000000"})
        assert r.status_code == 400
    r = await client.post("/auth/otp/verify", json={"phone": "09120000003", "code": "000000"})
    assert r.status_code == 429  # attempts exhausted


async def test_resend_cooldown(client, sms_outbox):
    r1 = await client.post("/auth/otp/request", json={"phone": "09120000004"})
    assert r1.status_code == 200
    r2 = await client.post("/auth/otp/request", json={"phone": "09120000004"})
    assert r2.status_code == 429
    assert r2.json()["detail"].startswith("otp_cooldown")


async def test_code_is_single_use(client, sms_outbox):
    await client.post("/auth/otp/request", json={"phone": "09120000005"})
    code = OTP_RE.search(sms_outbox[-1][1]).group(1)
    r1 = await client.post("/auth/otp/verify", json={"phone": "09120000005", "code": code})
    assert r1.status_code == 200
    r2 = await client.post("/auth/otp/verify", json={"phone": "09120000005", "code": code})
    assert r2.status_code == 400


async def test_refresh_rotates_and_detects_reuse(client, sms_outbox):
    await login(client, sms_outbox, "09120000006")
    old_refresh = client.cookies.get("refresh_token")

    r = await client.post("/auth/refresh")
    assert r.status_code == 204
    assert client.cookies.get("refresh_token") != old_refresh

    # replay the old refresh -> whole family revoked
    client.cookies.set("refresh_token", old_refresh)
    r = await client.post("/auth/refresh")
    assert r.status_code == 401

    r = await client.post("/auth/refresh")  # the "new" one is now revoked too
    assert r.status_code == 401


async def test_logout_clears_session(client, sms_outbox):
    await login(client, sms_outbox, "09120000007")
    await client.post("/auth/logout")
    me = await client.get("/auth/me")
    assert me.status_code == 401


async def test_csrf_required_for_mutations(client, sms_outbox):
    await login(client, sms_outbox, "09120000008")
    # bypass the auto-CSRF hook by sending an explicit empty header
    r = await client.patch(
        "/users/me", json={"display_name": "x"}, headers={"X-CSRF-Token": "wrong"}
    )
    assert r.status_code == 403
