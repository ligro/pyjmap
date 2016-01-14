from flask import Flask, request, Response, json, abort
from werkzeug.exceptions import BadRequest

import methods

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    """
    The only one API endpoint.
    """

    # this throw a BadRequest if json is not sent
    data = request.get_json()

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
    return Response(response=json.dumps(responses), mimetype='application/json')

@app.teardown_request
def teardown_request(exception):
    if exception is not None:
        app.logger.warning(exception)

def dispatch(method, args):
    try:
        for response in methods.__dict__[method](args):
            yield response
    except KeyError as e:
        yield ['error', {"type": "unknownMethod"}]
    except Exception as e:
        app.logger.warning([method, e])
        yield ['error', {"type": "unknownMethod"}]

if __name__ == '__main__':
    app.run(debug=True)
