"""Wishlist claim visibility matrix.

owner sees no claims · a claimed item shows "reserved" to *other* friends
(without revealing who) · only the claimer can release it.
"""

import pytest

from app.models import Friendship, FriendshipStatus
from tests.conftest import as_user

pytestmark = pytest.mark.asyncio


async def _befriend(db, a: int, b: int) -> None:
    db.add(Friendship(requester_id=a, addressee_id=b, status=FriendshipStatus.accepted))
    await db.commit()


async def test_visibility_matrix(client, db_session):
    owner = await as_user(client, db_session, "09120000201", "Owner")
    # owner adds 5 items
    ids = []
    for n in range(1, 6):
        r = await client.post("/wishlists/items", json={"title": f"item {n}", "position": n})
        assert r.status_code == 201
        ids.append(r.json()["id"])

    # owner's own view carries no claim fields at all
    mine = (await client.get("/wishlists/me")).json()
    assert {i["title"] for i in mine} == {f"item {n}" for n in range(1, 6)}
    assert all("is_claimed" not in i for i in mine)

    friend1 = await as_user(client, db_session, "09120000202", "F1")
    await _befriend(db_session, owner, friend1)

    # friend1 sees all 5, none claimed, then claims item #3
    view = (await client.get(f"/wishlists/{owner}")).json()
    assert len(view) == 5 and not any(i["is_claimed"] for i in view)
    r = await client.post(f"/wishlists/items/{ids[2]}/claim")
    assert r.status_code == 204

    v1 = {i["id"]: i for i in (await client.get(f"/wishlists/{owner}")).json()}
    assert v1[ids[2]]["is_claimed"] and v1[ids[2]]["claimed_by_me"]

    # friend2 sees item #3 reserved (but not by whom), the rest free
    friend2 = await as_user(client, db_session, "09120000203", "F2")
    await _befriend(db_session, owner, friend2)
    v2 = {i["id"]: i for i in (await client.get(f"/wishlists/{owner}")).json()}
    assert v2[ids[2]]["is_claimed"] is True
    assert v2[ids[2]]["claimed_by_me"] is False
    assert all(not v2[i]["is_claimed"] for i in ids if i != ids[2])
    assert "claimed_by" not in v2[ids[2]]

    # friend2 cannot double-claim it
    assert (await client.post(f"/wishlists/items/{ids[2]}/claim")).status_code == 409
    # ...nor release someone else's claim
    assert (await client.delete(f"/wishlists/items/{ids[2]}/claim")).status_code == 403

    # owner still sees nothing about claims
    await as_user(client, db_session, "09120000201")
    mine2 = (await client.get("/wishlists/me")).json()
    assert all("is_claimed" not in i for i in mine2)

    # the claimer can release it
    await as_user(client, db_session, "09120000202")
    assert (await client.delete(f"/wishlists/items/{ids[2]}/claim")).status_code == 204
    v3 = {i["id"]: i for i in (await client.get(f"/wishlists/{owner}")).json()}
    assert not v3[ids[2]]["is_claimed"]


async def test_non_friend_cannot_view_or_claim(client, db_session):
    owner = await as_user(client, db_session, "09120000210", "O")
    r = await client.post("/wishlists/items", json={"title": "thing"})
    item_id = r.json()["id"]

    await as_user(client, db_session, "09120000211", "Stranger")
    assert (await client.get(f"/wishlists/{owner}")).status_code == 403
    assert (await client.post(f"/wishlists/items/{item_id}/claim")).status_code == 403


async def test_owner_cannot_claim_own(client, db_session):
    owner = await as_user(client, db_session, "09120000220", "O")
    item_id = (await client.post("/wishlists/items", json={"title": "x"})).json()["id"]
    assert (await client.post(f"/wishlists/items/{item_id}/claim")).status_code == 403
    _ = owner
