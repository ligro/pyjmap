import traceback

from werkzeug.exceptions import BadRequest
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import Flask, request, Response, json, abort

from pyjmap.database import Device, User
from pyjmap import database, methods, auth

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
            # max age 5 minutes
            # FIXME should be moved to the config file
            tokenData = auth.getURLSafeSerializer().loads(data['token'], max_age=300)
        except SignatureExpired:
            return make_response(get_continuation_token_response(tokenData), status=401)
        except BadSignature:
            abort(403)

        try:
            user = User.query.filter_by(username=tokenData['username']).one()
            user.checkPwd(data['password'])
        except database.NoResultFound:
            return make_response(get_continuation_token_response(tokenData), status=401)
        except User.BadPassword:
            return make_response(get_continuation_token_response(tokenData), status=401)

        # getOrCreate
        device = Device()
        device.setFromArray(tokenData)
        device.userId = user.id
        device.save()
        database.commit()

        auth.setUserAndDevice(user, device)

        response = get_endpoints()
        response['accessToken'] = auth.createAccessToken();

        return make_response(response, status=201)

    return make_response(get_continuation_token_response(data))

def get_continuation_token_response(data):
    return {
        'continuationToken': auth.getURLSafeSerializer().dumps(data),
        'methods': ['password'],
        'prompt': None
    }

@app.route('/access-token', methods=['DELETE'])
def revoke_token():
    """
    Revoke the current access token.
    """
    auth.require_authorization()

    auth.current_device.delete()
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
