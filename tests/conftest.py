import pytest

from app import app

@pytest.fixture(scope="session")
def test_client():
    """The Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
