import importlib

from flask import request, abort, current_app
from mongoengine import NotUniqueError

from ..core.decorators import token_required

from ..models import get_user_model


@token_required
def POST_register():
    data = request.json

    try:
        User = get_user_model()
        user = User.create(**data)
    except NotUniqueError:
        abort(400, 'Email exists already')

    return user.to_dict(excluded='encrypted_password')


__all__ = [
    'POST_register',
]
