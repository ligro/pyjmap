from flask import json
import pytest

import pyjmap
import provider

def test_get_accounts(client):
    user = provider.user()
    accessToken = provider.getAccessTokenForUser(user)

    data = [
        ['getAccounts', {}, '#1']
    ]
    response = client.post('/', headers={'Authorization': accessToken}, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    responseData = json.loads(response.data)
    for resp in responseData:
        assert resp[0] == 'accounts'
        assert resp[2] == data[0][2]
        # no account
        assert len(resp[1]) == 0

