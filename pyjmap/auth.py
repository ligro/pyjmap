import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, request, abort

from pyjmap.database import User, Device
from pyjmap import database

current_user = None
current_device = None

# TODO make a decorator
def require_authorization():
    """
    Check the Authorization header contains a valid Access Token.
    """
    global current_user, current_device

    if 'Authorization' not in request.headers:
        abort(401)

    # check the access token is still valid
    try:
        # token is valid for 24 hours
        # FIXME should be moved to the config file
        tokenData = getURLSafeSerializer().loads(getAccessToken(), max_age=86400)
    except BadSignature:
        abort(401)

    try:
        device = Device.query.filter_by(id=tokenData['deviceId']).one()
    except database.NoResultFound:
        current_app.logger.debug(request.headers['Authorization'])
        abort(401)

    if device.userId != tokenData['userId'] or not isinstance(device.user, User):
        abort(401)

    current_device = device
    current_user = current_device.user
    if current_user is None:
        abort(401)

def getAccessToken():
    if 'Authorization' not in request.headers:
        return None

    return request.headers['Authorization']

def setUserAndDevice(user, device):
    global current_user, current_device
    current_user = user
    current_device = device

def createAccessToken():
    global current_user, current_device
    return _createAccessToken(current_user, current_device)

def _createAccessToken(user, device):
    data = {
        'userId': user.id,
        'deviceId': device.id,
        'salt': str(os.urandom(12)),
    }
    return getURLSafeSerializer().dumps(data)

def getURLSafeSerializer():
    # TODO store secret key in config and add a salt
    return URLSafeTimedSerializer('secret-key')


