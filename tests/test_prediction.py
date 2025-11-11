import pytest

API_PREFIX = "/api-deutsche"
AUTH_PREFIX = f"{API_PREFIX}/auth"
PREDICT_PREFIX = f"{API_PREFIX}/predict"


def _ensure_user(client, username, password):
    client.post(f"{AUTH_PREFIX}/register", json={"username": username, "password": password})


def _login_get_token(client, username, password):
    _ensure_user(client, username, password)
    r = client.post(f"{AUTH_PREFIX}/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestPredictions:
    def test_sample_inputs_expected_outputs(self, client):
        token = _login_get_token(client, "pred_user", "p")
        headers = _auth_header(token)

        cases = [
            (
                {
                    "longitude": -122.64,
                    "latitude": 38.01,
                    "housing_median_age": 36.0,
                    "total_rooms": 1336.0,
                    "total_bedrooms": 258.0,
                    "population": 678.0,
                    "households": 249.0,
                    "median_income": 5.5789,
                    "ocean_proximity": "NEAR OCEAN",
                },
                320201.58554044,
            ),
            (
                {
                    "longitude": -115.73,
                    "latitude": 33.35,
                    "housing_median_age": 23.0,
                    "total_rooms": 1586.0,
                    "total_bedrooms": 448.0,
                    "population": 338.0,
                    "households": 182.0,
                    "median_income": 1.2132,
                    "ocean_proximity": "INLAND",
                },
                58815.45033765,
            ),
            (
                {
                    "longitude": -117.96,
                    "latitude": 33.89,
                    "housing_median_age": 24.0,
                    "total_rooms": 1332.0,
                    "total_bedrooms": 252.0,
                    "population": 625.0,
                    "households": 230.0,
                    "median_income": 4.4375,
                    "ocean_proximity": "<1H OCEAN",
                },
                192575.77355635,
            ),
        ]

        for payload, expected in cases:
            r = client.post(f"{PREDICT_PREFIX}", json=payload, headers=headers)
            assert r.status_code == 200
            y = r.json()["prediction"]
            assert y == pytest.approx(expected, rel=1e-3)

    def test_predict_requires_auth(self, client):
        payload = {
            "longitude": -122.64,
            "latitude": 38.01,
            "housing_median_age": 36.0,
            "total_rooms": 1336.0,
            "total_bedrooms": 258.0,
            "population": 678.0,
            "households": 249.0,
            "median_income": 5.5789,
            "ocean_proximity": "NEAR OCEAN",
        }
        r = client.post(f"{PREDICT_PREFIX}", json=payload)
        assert r.status_code in (401, 403)

    def test_examples_from_dataset_rows(self, client):
        token = _login_get_token(client, "pred_user2", "p")
        headers = _auth_header(token)

        row1 = {
            "longitude": -122.23,
            "latitude": 37.88,
            "housing_median_age": 41.0,
            "total_rooms": 880.0,
            "total_bedrooms": 129.0,
            "population": 322.0,
            "households": 126.0,
            "median_income": 8.3252,
            "ocean_proximity": "NEAR BAY",
        }
        row2 = {
            "longitude": -122.22,
            "latitude": 37.86,
            "housing_median_age": 21.0,
            "total_rooms": 7099.0,
            "total_bedrooms": 1106.0,
            "population": 2401.0,
            "households": 1138.0,
            "median_income": 8.3014,
            "ocean_proximity": "NEAR BAY",
        }

        for payload in (row1, row2):
            r = client.post(f"{PREDICT_PREFIX}", json=payload, headers=headers)
            assert r.status_code == 200
            y = r.json()["prediction"]
            assert isinstance(y, float)
            assert 10000.0 <= y <= 1000000.0
