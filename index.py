from flask import Flask, request, Response, json, abort
from werkzeug.exceptions import BadRequest

import methods
import auth

app = Flask(__name__)

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
            return make_response(get_continuation_token(), status=401)

        # TODO check continuationToken
        # abort(403)

        if data['password'] != '42':
            return make_response(get_continuation_token(), status=401)

        response = get_endpoints()
        # TODO create a real access token
        response['accessToken'] = '42';

        return make_response(response, status=201)

    # TODO store them (now just used to raise BadRequest)
    data['username']
    data['clientName']
    data['clientVersion']
    data['deviceName']

    return make_response(get_continuation_token())

def get_continuation_token():
    return {
        'continuationToken': '24',
        'methods': ['password'],
        'prompt': None
    }


@app.route('/access-token', methods=['DELETE'])
def revoke_token():
    """
    Revoke the current access token.
    """
    auth.require_authorization()

    # TODO revoke the access token for real

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
    except Exception as e:
        app.logger.error([method, e])
        yield ['error', {"type": "technicalIssue"}]

if __name__ == '__main__':
    app.run(debug=True)
