from flask import json
import pytest

import pyjmap
import provider

def test_accounts(client):
    user = provider.user()
    accessToken = provider.getAccessTokenForUser(user)

    _test_getAccounts(client, accessToken, expectedNumber=0)

    data = [
        [
            'setAccounts',
            {
                'ifInState': {},
                'create': {},
                'update': {},
                'destroy': {}
            },
            '#1'
        ]
    ]
    response = client.post('/', headers={'Authorization': accessToken}, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    responseData = json.loads(response.data)

    for resp in responseData:
        assert resp[0] == 'accounts'
        assert resp[2] == data[0][2]
        assert len(resp[1]) == 8

    _test_getAccounts(client, accessToken, expectedNumber=0)

    data[0][1]['create'] = {
        "creationId": {
            'name': 'ligro daligro',
            'server': 'mail.daligro.net',
            'port': '997',
            'protocol': 'imaps'
        }
    }

    response = client.post('/', headers={'Authorization': accessToken}, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    responseData = json.loads(response.data)

    for resp in responseData:
        assert resp[0] == 'accounts'
        assert resp[2] == data[0][2]
        assert len(resp[1]) == 8
        assert len(resp[1]['created']) == 1

    _test_getAccounts(client, accessToken, expectedNumber=1)

def _test_getAccounts(client, accessToken, expectedNumber):
    data = [
        ['getAccounts', {}, '#1']
    ]
    response = client.post('/', headers={'Authorization': accessToken}, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200

    responseData = json.loads(response.data)
    pyjmap.app.logger.debug(responseData)
    for resp in responseData:
        assert resp[0] == 'accounts'
        assert resp[2] == data[0][2]
        assert len(resp[1]) == expectedNumber

    return responseData

