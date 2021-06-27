from webob import Request, Response
#from werkzeug.wrappers import Request, Response
import os
from jinja2 import Environment, FileSystemLoader
from inspect import isclass
# from whitenoise import WhiteNoise
from tools import *
from re import fullmatch


class API:
    def __init__(self, templates_dirs=['templates'], static_dir="static"):
        self.routes = {}
        self.templates_env = Environment(
            loader=FileSystemLoader([os.path.abspath(templates_dir) for templates_dir in templates_dirs]))
        self.exception_handler = None
        self.static_dir = static_dir
        # self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        # print("INITTTTTTTTTTTTTTTTTTTTTTTT")

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

    def template(self, template_name, context={}):
        return self.templates_env.get_template(template_name).render(**context).encode()

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
                            "Method now allowed", request.method)

                    handler(request, response, **kwargs)
                else:
                    handler(request, response, **kwargs)
            else:
                self.page404(request, response)
        except Exception as e:
            raise e
            # if self.exception_handler is None:
            #     raise e
            # else:
            #     print(e)
            #     self.exception_handler(request, response, e)

        # response.headers['Content-Length']

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = fullmatch(path, request_path)
            if parse_result is not None:
                return handler, parse_result.groupdict()

        return None, None