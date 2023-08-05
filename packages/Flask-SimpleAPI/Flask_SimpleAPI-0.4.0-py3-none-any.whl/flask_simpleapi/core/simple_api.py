import inspect
from importlib import import_module

from flask import Flask
from os import listdir
from .tools import my_import

class SimpleApi(Flask):
    """Override Flask for handling automatically apis

    - Override dispatch_request: catching all error and render as Json
    - register_api: for generating flask route from python module. See docs of register_api
    - print_urls: print all generated routes
    """

    _allowed_http_methods = ['POST', 'PUT', 'GET', 'DELETE']
    _allowed_socket_methods = ['ON']
    _url_rules = []

    def __init__(self, *args, api_root_path='', **kwargs):
        super(SimpleApi, self).__init__(*args, **kwargs)

        self.api_root_path = api_root_path

    def register_apis(self, module):
        """Register multi apis from apis folder, this is shorthand of multi register_api

        :param module: module python corresponding to package that contains apis
        """
        api_file_names = [f for f in listdir(module.__path__[0]) if '__' not in f]

        for n in api_file_names:
            api_name = n.replace('.py', '')
            api_module = import_module('{}.{}'.format(module.__name__ , api_name))
            self.register_api(api_module)

    def register_api(self, module, api_path=None):
        """Register api and generate Flask routes from python module

        :param module: python module which contains api endpoint view functions.
            Example: - GET_info() in api.product => [GET] /api/product/info
                     - POST_update(str_user_id) in api.user => [POST] /api/user/<string:str_user_id>
        """
        methods = self._allowed_http_methods + self._allowed_socket_methods
        names = [f for f in dir(module) if f.split('_', 1)[0] in methods]

        api_name = module.__name__.split('.')[-1]
        api_path = api_path or '/{}'.format(api_name)

        # # Create new blueprint by Api module
        # blueprint = Blueprint(module.__name__, __name__)

         # Register HTTP methods
        for name in names:
            method, view_name = name.split('_', 1)

            if method in self._allowed_socket_methods:
                socket_method = method
                view_func = getattr(module, name)

                if 'socketio' not in self.extensions:
                    raise ModuleNotFoundError('You have to install SocketIO: http://flask-socketio.readthedocs.io/en/latest/')

                self.extensions['socketio'].on_event(view_name, view_func, namespace='/{}'.format(api_name))

            elif method in self._allowed_http_methods:
                http_method = method

                view_func = getattr(module, name)
                rule = '{}{}/{}'.format(self.api_root_path, api_path, view_name)
                params = inspect.signature(view_func)
                str_params = self._build_str_params(params)

                if str_params:
                    rule = '{}/{}'.format(rule, str_params)

                url_rule = dict(
                    rule=rule,
                    endpoint='{}:{}'.format(api_name, view_name),
                    view_func=view_func,
                    methods=[http_method]
                )

                self.add_url_rule(**url_rule)
                self._url_rules.append(url_rule)

        # # Register blueprint to app
        # self.register_blueprint(blueprint)

    def _build_str_params(self, params):
        """Convert params tuple to format of Flask params
        Example: - (str_user_id) => <string:str_user_id>
                 - (str_user_id, float_price) => <string:str_user_id>/<float:float_price>

        :param params: (tuple) params tuple. (get from inspect.signature)
        :return: (string) params string of Flask url params. Ex: <string:str_user_id>/<float:float_price>
        """
        _params = []

        for p in params.parameters.values():
            param_type, param_name = p.name.split('_', 1)
            if param_type == 'str':
                param_type = 'string'

            param = '<{}:{}>'.format(param_type, p.name)
            _params.append(param)

        return '/'.join(_params)

    def print_urls(self):
        """Print all rules"""
        for rule in self._url_rules:
            print('{endpoint:40s} {methods[0]:8s} {rule}'.format(**rule))

