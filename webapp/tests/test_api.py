import pytest
from webapp.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_api_ordenes(client):
    rv = client.get("/ordenes/api/ordenes")
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)
