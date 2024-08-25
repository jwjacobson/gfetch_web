def test_get(test_client):
    response = test_client.get("/")
    
    assert response.status_code == 200