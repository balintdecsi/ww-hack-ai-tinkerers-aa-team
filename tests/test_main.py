def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Comics Factory' in response.data
