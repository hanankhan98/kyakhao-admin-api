"""AI Pick API quick test using FastAPI TestClient."""

from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth import create_token

client = TestClient(app)

# Admin user token (existing admin email from DB)
ADMIN_EMAIL = "lalainf247@gmail.com"
token = create_token({"sub": ADMIN_EMAIL, "role": "admin"})
headers = {"Authorization": f"Bearer {token}"}


def test_get_preferences():
    print("\n=== 1. GET /ai-pick/preferences ===")
    resp = client.get("/ai-pick/preferences", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert "spicy_levels" in data
    assert "cuisines" in data
    assert "budget_min" in data
    assert "budget_max" in data
    print("[PASS] GET passed")
    return data


def test_update_preferences():
    print("\n=== 2. PUT /ai-pick/preferences ===")
    payload = {
        "cuisines": ["Italian", "Mexican", "Indian", "Chinese"],
        "budget_max": 120,
        "spice_preference": "no_spicy",
        "suggest_new_cuisines": False,
        "spicy_levels": [
            {"name": "Mild", "order": 1},
            {"name": "Hot", "order": 2},
        ],
    }
    resp = client.put("/ai-pick/preferences", json=payload, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cuisines"] == ["Italian", "Mexican", "Indian", "Chinese"]
    assert data["budget_max"] == 120
    assert data["spice_preference"] == "no_spicy"
    assert data["suggest_new_cuisines"] is False
    print("[PASS] PUT passed")


def test_reset_preferences():
    print("\n=== 3. POST /ai-pick/preferences/reset ===")
    resp = client.post("/ai-pick/preferences/reset", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cuisines"] == ["Italian", "Mexican", "Indian"]
    assert data["budget_max"] == 50
    assert data["spice_preference"] == "spicy"
    print("[PASS] RESET passed")


def test_unauthorized():
    print("\n=== 4. GET without auth ===")
    resp = client.get("/ai-pick/preferences")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 403
    print("[PASS] Unauthorized blocked")


if __name__ == "__main__":
    try:
        test_get_preferences()
        test_update_preferences()
        test_reset_preferences()
        test_unauthorized()
        print("\nALL AI PICK API TESTS PASSED!")
    except AssertionError as e:
        print(f"\nTest assertion failed: {e}")
    except Exception as e:
        print(f"\nTest error: {e}")
