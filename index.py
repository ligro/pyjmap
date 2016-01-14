from flask import Flask, request, Response, json
from error import Error

import methods

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    """
    The only one API endpoint.
    """
    # curl -H 'Content-Type: application/json' -v 'http://localhost:5000/' -d '[["method1", {"arg1": "arg1data", "arg2": "arg2data"}, "#1"],["method2", {"arg1": "arg1data"}, "#2"],["method3", {}, "#3"]]'
    responses = []
    for params in request.get_json():
        app.logger.debug(params)
        method = params[0]
        arguments = params[1]
        methodId = params[2]
        for res in dispatch(method, arguments):
            app.logger.debug(res)
            res.append(methodId)
            responses.append(res)

    app.logger.debug(json.dumps(responses))
    return Response(response=json.dumps(responses), mimetype='application/json')

@app.route('/error')
def error():
    raise Error('An error occured', status_code=503)

@app.teardown_request
def teardown_request(exception):
    if exception is not None:
        app.logger.warning(exception)

def dispatch(method, args):
    try:
        for response in methods.__dict__[method](args):
            yield response
    except Exception as e:
        if e == method:
            e = unknownMethod
        app.logger.warning([method, e])
        yield ['error', {"type": "unknownMethod"}]

if __name__ == '__main__':
    app.run(debug=True)