import pytest
from flask import json

import pyjmap

def setup_module(self):
    pyjmap.app.app_context().push()
    pyjmap.database.db.drop_all()
    pyjmap.database.db.create_all()

@pytest.fixture
def app():
    pyjmap.app.testing = True
    pyjmap.app.debug = True

    return pyjmap.app

def test_endpoint_not_loggued(client):
    response = client.get('/endpoints')
    assert response.status_code == 401

class Provider:

    def user(username, password):
        user = pyjmap.database.User()
        user.username = username
        user.setPassword(password)
        user.save()
        pyjmap.database.commit()
        return user


@pytest.mark.usefixtures('client_class')
class TestAccessToken:
    """Tests related to the /access-token routes."""

    def test_empty_param(self):
        """Call with no parameter."""
        response = self.client.post('/access-token')
        assert response.status_code == 400

    def test_retrieve(self):
        """Access token retrieving workflow, without error."""
        # todo add a user
        password = 'testpassword'
        user = Provider.user('testuser', password)

        data = {
            'username' : user.username,
            'clientVersion' : '2.8.7',
            'clientName' : 'py.test',
            'devicename' : 'terminal'
        }
        response = self.client.post('/access-token', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        self._assert_access_token_step1_response(data)

        data = {
            'method' : 'password',
            'token' : data['continuationToken'],
            'password' : password
        }
        response = self.client.post('/access-token', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'accessToken' in data
        accessToken = data['accessToken']

        response = self.client.get('/endpoints', headers={'Authorization': accessToken})
        assert response.status_code == 200

        response = self.client.delete('/access-token', headers={'Authorization': accessToken})
        assert response.status_code == 204

        response = self.client.get('/endpoints', headers={'Authorization': accessToken})
        assert response.status_code == 401

    def test_empty_parameter(self):
        """Check bad parameters returns bad response."""
        pass

    def test_expired_continuation_token(self):
        """Response whe continuation token is expired."""
        pass

    def test_bad_continuation_token(self):
        """Response whe continuation token is expired."""
        pass

    def test_bad_user_not_found(self):
        """Response whe continuation token is expired."""
        pass

    def test_bad_password(self):
        """Response whe continuation token is expired."""
        pass

    def _assert_access_token_step1_response(self, data):
        """Assert access token response, with continuation token."""
        assert 'continuationToken' in data
        assert 'methods' in data
        assert len(data['methods']) == 1
        assert 'password' in data['methods']
        assert 'prompt' in data

@pytest.mark.usefixtures('client_class')
class TestEndpoints:

    def test_loggued_out(self):
        """Call with no parameter."""
        response = self.client.get('/endpoints')
        assert response.status_code == 401
