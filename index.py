import traceback

from werkzeug.exceptions import BadRequest
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, request, Response, json, abort

from database import Device, User
import database
import methods
import auth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ligro@localhost/pyjmap'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
database.db.init_app(app)

@app.route('/', methods=['POST'])
def index():
    """
    The only one API endpoint.
    """

    # this throw a BadRequest if json is not sent
    data = request.get_json()

    auth.require_authorization()

    # check json format
    for params in data:
        if len(params) != 3:
            raise BadRequest(description="Json format doesn't follow jmap specification. Not enough arguments")

        if type(params[1]) is not dict:
            raise BadRequest(description="Json format doesn't follow jmap specification. Arguments must be an Object.")

    responses = []
    for params in data:
        [method, arguments, methodId] = params
        for res in dispatch(method, arguments):
            res.append(methodId)
            responses.append(res)

    app.logger.debug(json.dumps(responses))
    return make_response(responses)

@app.route('/endpoints', methods=['GET'])
def endpoints():
    # this throw a BadRequest if json is not sent
    data = request.get_json()

    auth.require_authorization()

    return make_response(get_endpoints())

@app.route('/access-token', methods=['POST'])
def access_token():
    """
    Generate an access token. Also do the password check.
    Do not handle rate limit.
    """
    # this throw a BadRequest if json is not sent
    data = request.get_json()

    if 'method' in data:
        if data['method'] != 'password':
            return make_response(get_continuation_token_response(data), status=401)

        try:
            tokenData = _getURLSafeSerializer().loads(data['token'])
        except BadSignature:
            abort(403)

        try:
            user = User.query.filter_by(username=tokenData['username']).one()
            user.checkPwd(data['password'])
        except database.NoResultFound:
            return make_response(get_continuation_token_response(tokenData), status=401)
        except User.BadPassword:
            return make_response(get_continuation_token_response(tokenData), status=401)

        auth.setUser(user)

        device = Device()
        device.setFromArray(tokenData)
        device.userId = user.id
        device.accessToken = auth.createAccessToken()
        device.save()
        database.commit()

        response = get_endpoints()
        response['accessToken'] = device.accessToken;

        return make_response(response, status=201)

    return make_response(get_continuation_token_response(data))

def get_continuation_token_response(data):
    return {
        'continuationToken': _getURLSafeSerializer().dumps(data),
        'methods': ['password'],
        'prompt': None
    }

def _getURLSafeSerializer():
    return URLSafeTimedSerializer('secret-key')

@app.route('/access-token', methods=['DELETE'])
def revoke_token():
    """
    Revoke the current access token.
    """
    auth.require_authorization()


    try:
        device = Device.getByAccessToken(auth.getAccessToken())
    except database.NoResultFound:
        abort(401)

    device.delete()
    database.commit()

    return Response(status=204)

def get_endpoints():
    return {
        'api' : '/',
        'eventSource' : None,
        'upload' : None,
        'download' : None,
    }

def make_response(data, status=200):
    return Response(response=json.dumps(data), status=status, mimetype='application/json')

@app.teardown_request
def teardown_request(exception):
    if exception is not None:
        app.logger.warning(exception)

def dispatch(method, args):
    try:
        for response in methods.__dict__[method](**args):
            yield response
    except KeyError as e:
        yield ['error', {"type": "unknownMethod"}]
    except methods.MethodException as e:
        yield ['error', {"type": str(e)}]
    except Exception:
        app.logger.error(method)
        app.logger.error(traceback.format_exc())
        yield ['error', {"type": "technicalIssue"}]

if __name__ == '__main__':
    app.run(debug=True)
