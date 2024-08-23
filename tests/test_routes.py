import pytest
import ipdb

from app import app

@pytest.fixture
def test_client():
    # Flask provides a test client you can use to simulate requests
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

