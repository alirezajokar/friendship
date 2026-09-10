import pytest

from app.core import ratelimit
from tests.conftest import login, set_profile

pytestmark = pytest.mark.asyncio


async def _fresh_login(client, sms_outbox, phone, name):
    ratelimit.reset()
    await login(client, sms_outbox, phone)
    await set_profile(client, name)


async def test_invite_accept_creates_request_then_accept(client, sms_outbox):
    # User A registers and grabs an invite link
    await _fresh_login(client, sms_outbox, "09120000101", "Ali")
    invite = (await client.get("/invites/me")).json()
    code = invite["code"]
    assert invite["url"].endswith(f"/i/{code}")
    await client.post("/auth/logout")

    # Public preview works without auth
    ratelimit.reset()
    prev = await client.get(f"/i/{code}")
    assert prev.status_code == 200
    assert prev.json()["inviter"]["display_name"] == "Ali"

    # User B registers and accepts the invite -> pending request to A
    await _fresh_login(client, sms_outbox, "09120000102", "Sara")
    acc = await client.post(f"/invites/{code}/accept")
    assert acc.status_code == 200
    assert acc.json()["status"] == "pending"
    b_id = (await client.get("/auth/me")).json()["id"]
    await client.post("/auth/logout")

    # A sees the incoming request and accepts it
    ratelimit.reset()
    await login(client, sms_outbox, "09120000101")
    reqs = (await client.get("/friends/requests")).json()
    assert len(reqs) == 1 and reqs[0]["requester"]["display_name"] == "Sara"
    r = await client.post(f"/friends/requests/{reqs[0]['id']}/respond", json={"accept": True})
    assert r.status_code == 200 and r.json()["status"] == "accepted"

    friends = (await client.get("/friends")).json()
    assert [f["id"] for f in friends] == [b_id]


async def test_cannot_accept_own_invite(client, sms_outbox):
    await _fresh_login(client, sms_outbox, "09120000103", "Solo")
    code = (await client.get("/invites/me")).json()["code"]
    r = await client.post(f"/invites/{code}/accept")
    assert r.status_code == 422


async def test_regenerate_changes_code(client, sms_outbox):
    await _fresh_login(client, sms_outbox, "09120000104", "Reg")
    c1 = (await client.get("/invites/me")).json()["code"]
    c2 = (await client.post("/invites/regenerate")).json()["code"]
    assert c1 != c2
    assert (await client.get(f"/i/{c1}")).status_code == 404
