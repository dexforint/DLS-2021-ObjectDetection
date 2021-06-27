from webob import Request, Response
from inspect import isclass
from re import fullmatch
import json

def POSTprocessing(POST):
    if 'json' in POST:
        obj = json.loads(POST['json'])
        for key, value in obj.items():
            POST[key] = value

        del POST['json']


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        POSTprocessing(request.POST)
        response = Response()


        # if session['is_user']:
        #     request.user = get_users_info([session['uid']])[session['uid']]
        # else:
        #    request.user = None
        self.request = request

        self.handle_request(request, response)
        return response(environ, start_response)

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler


    def add_route(self, path, handler):
        assert path not in self.routes, "Such route already exists."
        self.routes[path] = handler

    def route(self, path):
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def handle_request(self, request, response):
        handler, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler is not None:
                if isclass(handler):
                    handler = getattr(
                        handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError(
                            "Method now allowed!", request.method)

                    handler(request, response, **kwargs)
                else:
                    handler(request, response, **kwargs)
            else:
                self.page404(request, response)
        except Exception as e:
            raise e

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = fullmatch(path, request_path)
            if parse_result is not None:
                return handler, parse_result.groupdict()

        return None, None
