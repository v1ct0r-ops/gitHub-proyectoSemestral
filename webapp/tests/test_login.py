import pytest
from webapp.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_login_page(client):
    rv = client.get("/login/")
    assert rv.status_code == 200
    assert b"Iniciar" in rv.data
