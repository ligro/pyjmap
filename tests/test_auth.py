import pytest
from flask import json

import pyjmap

@pytest.fixture
def app():
    pyjmap.app.app_context().push()
    pyjmap.app.testing = True
    pyjmap.app.debug = True
    return pyjmap.app

def test_endpoint_not_loggued(client):
    response = client.get('/endpoints')
    assert response.status_code == 401

def test_access_token_empty(client):
    response = client.post('/access-token')
    assert response.status_code == 400

def test_access_token(client):
    data = {
        'username' : 'ligro',
        'clientVersion' : '2.8.7',
        'clientName' : 'py.test',
        'devicename' : 'terminal'
    }
    response = client.post('/access-token', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

if __name__ == '__main__':
    unittest.main()

