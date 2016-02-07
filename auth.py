from flask import current_app, request, abort
from database import User, Device
import database

current_user = None

# TODO make a decorator
def require_authorization():
    """
    Check the Authorization header contains a valid Access Token.
    """
    global current_user

    if 'Authorization' not in request.headers:
        current_app.logger.debug(request.headers)
        abort(401)

    # check the access token is still valid
    try:
        device = Device.getByAccessToken(getAccessToken())
    except database.NoResultFound:
        current_app.logger.debug(request.headers['Authorization'])
        abort(401)

    if not isinstance(device.user, User):
        abort(401)

    current_user = device.user
    if current_user is None:
        abort(401)

def getAccessToken():
    if 'Authorization' not in request.headers:
        return None

    return request.headers['Authorization']

def setUser(user):
    global current_user
    current_user = user

def createAccessToken():
    return 42
