from flask import jsonify, Response, request, current_app
from mongoengine import FieldDoesNotExist
from werkzeug.exceptions import HTTPException


class JsonResponse(Response):
    """Render Json if object is dict, list, MongoEngine object"""

    @classmethod
    def force_type(cls, res, environ=None):
        # Only convert to Json if content_type is json
        if request.path.startswith(current_app.api_root_path):
                # and request.content_type == 'application/json':

            if isinstance(res, HTTPException):
                code = res.code
                res = jsonify({'code': code, 'error': res.description})
                res.status_code = code

            elif isinstance(res, (dict, list)):
                res = jsonify(res)

        elif isinstance(res, (dict, list)):
            res = jsonify(res)

        return super(JsonResponse, cls).force_type(res, environ)
