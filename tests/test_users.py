import pytest

API_PREFIX = "/api-deutsche"
AUTH_PREFIX = f"{API_PREFIX}/auth"
USERS_PREFIX = f"{API_PREFIX}/users"


def _register(client, username, password):
    return client.post(f"{AUTH_PREFIX}/register", json={"username": username, "password": password})


def _login_json_get_token(client, username, password):
    r = client.post(f"{AUTH_PREFIX}/login", json={"username": username, "password": password})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    return body["access_token"]


def _login_form_get_token(client, username, password):
    r = client.post(f"{AUTH_PREFIX}/login-with-token", data={"username": username, "password": password})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    return body["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    try:
        from app.core.rate_limit import limiter
        limiter.storage.clear()
    except Exception:
        pass
    yield
    try:
        from app.core.rate_limit import limiter
        limiter.storage.clear()
    except Exception:
        pass


def test_register_and_login_flow(client):
    r = _register(client, "alice", "secret")
    assert r.status_code in (200, 201)
    user_id = r.json().get("user_id")
    assert user_id is not None

    r2 = _register(client, "alice", "x")
    assert r2.status_code in (200, 400, 409)
    if r2.status_code == 200:
        assert "error" in r2.json()

    token = _login_json_get_token(client, "alice", "secret")
    r = client.get(f"{AUTH_PREFIX}/me", headers=_auth_header(token))
    assert r.status_code == 200
    assert r.json()["id"] == user_id


def test_change_password_and_login_with_new_password(client):
    r = _register(client, "bob", "old")
    assert r.status_code in (200, 201)
    bob_id = r.json()["user_id"]

    token = _login_json_get_token(client, "bob", "old")
    headers = _auth_header(token)

    r = client.patch(f"{AUTH_PREFIX}/change-password/{bob_id}", json={"old_password": "old", "new_password": "newpass"}, headers=headers)
    assert r.status_code == 200

    token2 = _login_json_get_token(client, "bob", "newpass")
    assert isinstance(token2, str)

    r = client.patch(f"{AUTH_PREFIX}/change-password/{bob_id}", json={"old_password": "WRONG", "new_password": "x"}, headers=_auth_header(token2))
    assert r.status_code in (400, 404)


def test_admin_reset_password_all_good(client):
    r = _register(client, "carol", "p1")
    assert r.status_code in (200, 201)
    carol_id = r.json()["user_id"]

    token = _login_json_get_token(client, "carol", "p1")
    headers = _auth_header(token)

    r = client.patch(f"{AUTH_PREFIX}/admin/reset-password/{carol_id}", json={"new_password": "p2"}, headers=headers)
    assert r.status_code == 200

    token2 = _login_json_get_token(client, "carol", "p2")
    assert isinstance(token2, str)


def test_users_list_get_update_delete(client):
    a = _register(client, "u1", "x").json()
    b = _register(client, "u2", "y").json()
    u1_id, u2_id = a["user_id"], b["user_id"]

    token = _login_json_get_token(client, "u1", "x")
    headers = _auth_header(token)

    r = client.get(f"{USERS_PREFIX}", headers=headers)
    assert r.status_code == 200
    ids = {u["id"] for u in r.json()}
    assert u1_id in ids and u2_id in ids

    r = client.get(f"{USERS_PREFIX}/{u1_id}", headers=headers)
    assert r.status_code == 200

    r = client.patch(f"{USERS_PREFIX}/{u2_id}", json={"username": "u2_new"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "u2_new"

    r = client.delete(f"{USERS_PREFIX}/{u1_id}", headers=headers)
    assert r.status_code == 200

    r = client.get(f"{USERS_PREFIX}/{u1_id}", headers=headers)
    assert r.status_code == 404


def test_delete_all_users(client):
    for i in range(3):
        _register(client, f"x{i}", "p")

    token = _login_json_get_token(client, "x0", "p")
    headers = _auth_header(token)

    r = client.delete(f"{USERS_PREFIX}", headers=headers)
    assert r.status_code == 200
    assert r.json()["deleted"] >= 1

    r = client.get(f"{USERS_PREFIX}", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_login_rate_limit_only_on_form_endpoint(client):
    _register(client, "rate_user", "p")

    ok = 0
    last_status = None
    for i in range(11):
        resp = client.post(f"{AUTH_PREFIX}/login-with-token", data={"username": "rate_user", "password": "p"})
        last_status = resp.status_code
        if last_status == 200:
            ok += 1
        elif last_status == 429:
            break
    assert ok >= 1
    assert last_status == 429

    resp2 = client.post(f"{AUTH_PREFIX}/login", json={"username": "rate_user", "password": "p"})
    assert resp2.status_code == 200
