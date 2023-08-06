from flask import request, current_app, abort
from mongoengine.errors import DoesNotExist

from ..models import get_session_model, get_user_model
from ..core.decorators import login_required, token_required


def GET_init():
    """Special endpoint for init the whole session

    :param token: (str) (GET) Token string

    :return: (str) Session id
    """
    Session = get_session_model()

    token = request.args.get('token')
    session = None

    if current_app.config.get('SOCKET_ACTIVE'):
        socket = request.args.get('socket', None)

    # If session still exists then update the datetime and return at
    if token:
        try:
            session = Session.objects.get(pk=token)

            if current_app.config.get('SOCKET_ACTIVE'):
                session.socket = socket

            session.update_datetime()
            session.save()

        except DoesNotExist:
            pass

    # When token is expired, does not exist ... then create a new one
    if not session:
        session = Session()
        if current_app.config.get('SOCKET_ACTIVE'):
            session.socket = socket

        session.save()

    return session.to_dict(prefetch='user', excluded='user.encrypted_password')


@token_required
def GET_current():
    return request.session.to_dict(prefetch='user', excluded='user.encrypted_password')


@token_required
def POST_login():
    User = get_user_model()

    data = request.json
    user = User.authenticate(**data)

    if not user:
        abort(404, 'User not found or password is not correct')

    session = request.session
    session.user = user
    session.save()

    return user.to_dict(excluded='encrypted_password')



@login_required
def GET_logout():
    """Logout user"""
    session = request.session

    session.user = None
    session.save()

    return session.to_dict()


__all__ = [
    'GET_logout',
    'POST_login',
    'GET_init',
    'GET_current',
]
