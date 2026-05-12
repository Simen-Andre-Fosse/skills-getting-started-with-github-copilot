def test_root_redirect(client):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # From the code, 9 activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post("/activities/Chess Club/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate(client):
    """Test signup when already signed up"""
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "duplicate@example.com"})
    # Second signup
    response = client.post("/activities/Chess Club/signup", params={"email": "duplicate@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]


def test_remove_participant_success(client):
    """Test successful removal of participant"""
    # First add a participant
    client.post("/activities/Programming Class/signup", params={"email": "remove@example.com"})
    # Then remove
    response = client.delete("/activities/Programming Class/participants", params={"email": "remove@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered remove@example.com from Programming Class" in data["message"]

    # Verify removed
    response = client.get("/activities")
    activities = response.json()
    assert "remove@example.com" not in activities["Programming Class"]["participants"]


def test_remove_participant_not_found(client):
    """Test removing non-existent participant"""
    response = client.delete("/activities/Chess Club/participants", params={"email": "nonexistent@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]


def test_remove_participant_activity_not_found(client):
    """Test removing participant from non-existent activity"""
    response = client.delete("/activities/NonExistent/participants", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]