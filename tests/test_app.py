from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path.endswith("/static/index.html")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "description" in activities["Chess Club"]

def test_signup_flow():
    activity = "Chess Club"
    email = "test_user@example.com"

    # 1. Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}

    # 2. Verify added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]

    # 3. Duplicate signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"

    # 4. Unregister
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}

    # 5. Verify removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]

    # 6. Unregister not signed up
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up"

def test_invalid_activity():
    response = client.post("/activities/InvalidActivity/signup?email=test@example.com")
    assert response.status_code == 404
