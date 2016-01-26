from flask import current_app, request, abort
current_user = None

# TODO make a decorator
def require_authorization():
    """
    Check the Authorization header contains a valid Access Token.
    """
    if 'Authorization' not in request.headers:
        current_app.logger.debug(request.headers)
        abort(401)

    # check the access token is still valid
    # TODO retrieve the good header
    if request.headers['Authorization'] != "42":
        current_app.logger.debug(request.headers['Authorization'])
        abort(401)


    current_user = 1
