def test_dashboard_redirect_for_anonymous(client):
    response = client.get('/', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Dashboard" not in response.data