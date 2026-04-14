from urllib.parse import quote


def activity_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_known_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200

    payload = response.json()

    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_student(client):
    email = "new.student@mergington.edu"

    response = client.post(activity_path("Chess Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_for_activity_rejects_duplicate_student(client):
    response = client.post(
        activity_path("Chess Club"),
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_for_unknown_activity_returns_not_found(client):
    response = client.post(
        activity_path("Unknown Club"),
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_removes_student(client):
    email = "michael@mergington.edu"

    response = client.delete(activity_path("Chess Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_from_unknown_activity_returns_not_found(client):
    response = client.delete(
        activity_path("Unknown Club"),
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_for_student_not_signed_up_returns_not_found(client):
    response = client.delete(
        activity_path("Chess Club"),
        params={"email": "not.registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}