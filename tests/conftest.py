import pytest
from minha_app import create_app, db
from minha_app.models import User, Purchase

@pytest.fixture()
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def test_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()

@pytest.fixture()
def test_user2(app):
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('password456')
        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()

@pytest.fixture()
def logged_in_client(client, test_user):
    client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password123'
    }, follow_redirects=True)

    yield client
