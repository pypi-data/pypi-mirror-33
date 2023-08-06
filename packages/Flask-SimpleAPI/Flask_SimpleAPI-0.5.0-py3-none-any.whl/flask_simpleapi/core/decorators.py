# -*- coding: utf-8 -*-
from functools import wraps
from uuid import UUID

from flask import request, abort
from mongoengine.errors import DoesNotExist
from ..models import get_session_model


def _detect_session():
    Session = get_session_model()
    token = request.args.get('token')

    if not token:
        abort(400, 'Token is required')

    if not Session.verify(token):
        abort(400, 'Token is not valid')

    # If token is valid then check in DB
    try:
        stored_session = Session.objects.get(id=UUID(token))
    except DoesNotExist:
        abort(400, 'Session does not exist')

    # Update expiration
    stored_session.update_datetime()
    stored_session.save()

    return stored_session


def token_required(f):
    """Specify that an endpoint need a token and a valid session

    :return: inject session object to request
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session = _detect_session()
        request.session = session

        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """Specify that an endpoint need a login session

    :return: inject session and user object to request
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session = _detect_session()
        user = session.user

        if not user:
            abort(403, 'You must be authenticated')

        request.user = user
        request.session = session

        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Specify that an endpoint need a anonymous session
    :return: inject session and user object to request
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session = _detect_session()
        user = session.user

        if user:
            abort(403, 'You must be anonymous')

        request.session = session

        return f(*args, **kwargs)
    return decorated_function


def perm_required(perm):
    def wrap(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session = _detect_session()

            request.session = session
            request.user = session.user

            if not request.user.has_perm(perm):
                abort(403, 'You are not allowed to do this')

            return f(*args, **kwargs)

        return decorated_function
    return wrap
