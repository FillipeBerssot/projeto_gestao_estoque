def test_request_login_page(client):
    response = client.get('/auth/login')

    assert response.status_code == 200
    assert b"Login" in response.data

def test_dashboard_redirect_for_anonymous(client):
    response = client.get('/', follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Dashboard" not in response.data

def test_successful_login(client, test_user):
    response_login = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password123'
    }, follow_redirects=True)

    assert response_login.status_code == 200
    assert b"Dashboard" in response_login.data
    assert b"Sair" in response_login.data

    response_logout = client.get('/auth/logout', follow_redirects=True)

    assert response_logout.status_code == 200
    assert b"desconectado com sucesso" in response_logout.data
    assert b"Sair" not in response_logout.data