import ipdb

def test_get(test_client):
    response = test_client.get("/")
    
    assert response.status_code == 200

def test_post_empty_request(test_client):
    response = test_client.post("/")

    assert response.status_code == 400