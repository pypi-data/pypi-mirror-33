from importlib import import_module

from ..core.tools import my_import


def get_user_model():
    settings = import_module('settings')
    user_model_str = getattr(settings, 'USER_MODEL', None)

    # If USER_MODEL is not defined then use the default one in core
    if not user_model_str:
        from .base_user import BaseUser
        class User(BaseUser):
            ...
        return User

    # If USER_MODEL is defined then use custom model
    return my_import(user_model_str)


def get_session_model():
    settings = import_module('settings')
    session_model_str = getattr(settings, 'SESSION_MODEL', None)

    # If SESSION_MODEL is not defined then use the default one in core
    if not session_model_str:
        from .base_session import BaseSession
        class Session(BaseSession):
            ...
        return Session

    # If SESSION_MODEL is defined then use custom model
    return my_import(user_model_str)
