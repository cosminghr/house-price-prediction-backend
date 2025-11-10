import pytest

API_PREFIX = "/api-deutsche"
AUTH_PREFIX = f"{API_PREFIX}/auth"
USERS_PREFIX = f"{API_PREFIX}/users"


def test_register_and_login_flow(client):
    r = client.post(f"{AUTH_PREFIX}/register", json={"username": "alice", "password": "secret"})
    assert r.status_code in (200, 201)
    user_id = r.json().get("user_id")
    assert user_id is not None

    r2 = client.post(f"{AUTH_PREFIX}/register", json={"username": "alice", "password": "x"})

    assert r2.status_code in (200, 400, 409)
    if r2.status_code == 200:
        assert "error" in r2.json()

    r = client.post(f"{AUTH_PREFIX}/login", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    assert r.json().get("user_id") == user_id


def test_change_password_and_login_with_new_password(client):
    r = client.post(f"{AUTH_PREFIX}/register", json={"username": "bob", "password": "old"})
    assert r.status_code in (200, 201)
    bob_id = r.json()["user_id"]

    r = client.patch(
        f"{AUTH_PREFIX}/change-password/{bob_id}",
        json={"old_password": "old", "new_password": "newpass"},
    )
    assert r.status_code == 200

    r = client.post(f"{AUTH_PREFIX}/login", json={"username": "bob", "password": "newpass"})
    assert r.status_code == 200

    r = client.patch(
        f"{AUTH_PREFIX}/change-password/{bob_id}",
        json={"old_password": "WRONG", "new_password": "x"},
    )
    assert r.status_code in (400, 404)  # tu arunci 400 pentru "bad_old"


def test_admin_reset_password_all_good(client):
    r = client.post(f"{AUTH_PREFIX}/register", json={"username": "carol", "password": "p1"})
    assert r.status_code in (200, 201)
    carol_id = r.json()["user_id"]

    r = client.patch(f"{AUTH_PREFIX}/admin/reset-password/{carol_id}", json={"new_password": "p2"})
    assert r.status_code == 200

    r = client.post(f"{AUTH_PREFIX}/login", json={"username": "carol", "password": "p2"})
    assert r.status_code == 200


def test_users_list_get_update_delete(client):
    a = client.post(f"{AUTH_PREFIX}/register", json={"username": "u1", "password": "x"}).json()
    b = client.post(f"{AUTH_PREFIX}/register", json={"username": "u2", "password": "y"}).json()
    u1_id, u2_id = a["user_id"], b["user_id"]

    r = client.get(f"{USERS_PREFIX}")
    assert r.status_code == 200
    users = r.json()
    ids = {u["id"] for u in users}
    assert u1_id in ids and u2_id in ids

    r = client.get(f"{USERS_PREFIX}/{u1_id}")
    assert r.status_code == 200
    assert r.json()["id"] == u1_id

    r = client.patch(f"{USERS_PREFIX}/{u2_id}", json={"username": "u2_new"})
    assert r.status_code == 200
    assert r.json()["username"] == "u2_new"

    r = client.delete(f"{USERS_PREFIX}/{u1_id}")
    assert r.status_code == 200
    r = client.get(f"{USERS_PREFIX}/{u1_id}")
    assert r.status_code == 404


def test_delete_all_users(client):
    for i in range(3):
        client.post(f"{AUTH_PREFIX}/register", json={"username": f"x{i}", "password": "p"})

    r = client.delete(f"{USERS_PREFIX}")
    assert r.status_code == 200
    count_deleted = r.json()["deleted"]
    assert count_deleted >= 1

    r = client.get(f"{USERS_PREFIX}")
    assert r.status_code == 200
    assert r.json() == []
