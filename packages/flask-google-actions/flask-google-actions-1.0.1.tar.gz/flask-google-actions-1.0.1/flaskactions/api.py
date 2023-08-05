from flask import Flask, request, abort
from flask_basicauth import BasicAuth
from googleactions import AppRequest, AppResponse

app = Flask(__name__)
basic_auth = BasicAuth(app)
functions = []


class Listeners(object):
    request_listener = None
    response_listener = None

    @staticmethod
    def request(app_request):
        Listeners.request_listener(app_request) if Listeners.request_listener else None

    @staticmethod
    def response(app_response):
        Listeners.response_listener(app_response) if Listeners.response_listener else None


@app.route('/', methods=['POST'])
@basic_auth.required
def web_hook():
    app_request = AppRequest(request.data)
    Listeners.request(app_request)
    func = get_function(app_request)
    if func:
        items = func(app_request)
        app_response = AppResponse(items, app_request)
        Listeners.response(app_response)
        return app_response.json()
    else:
        return abort(400)


def get_function(app_request):
    call = None
    for func in functions:
        if app_request.is_intent(func[1]):
            call = func[0]
    return call


def intent(name):
    def decorator(f):
        functions.append((f, name))
        return f
    return decorator


def listen(request_function=None, response_function=None):
    Listeners.request_listener = request_function
    Listeners.response_listener = response_function


def start(username, password, debug=True, port=5000):
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.run(debug=debug, port=port)
