from uuid import uuid4, UUID

from datetime import datetime

from flask import current_app
from mongoengine import UUIDField, ReferenceField

from ..core.model import TimestampedModel
from ..core.tools import my_import
from . import get_user_model


class BaseSession(TimestampedModel):
    id = UUIDField(primary_key=True, default=uuid4)
    user = ReferenceField(get_user_model())

    meta = {
        'abstract': True
    }

    @property
    def is_authenticated(self):
        return bool(self.user)

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    @staticmethod
    def verify(token):
        """Validate token and return if it's correct or return False"""

        try:
            val = UUID(token, version=4)
        except ValueError as e:
            # If it's a value error, then the string
            # is not a valid hex code for a UUID.
            return False

        # If the uuid_string is a valid hex code,
        # but an invalid uuid4,
        # the UUID.__init__ will convert it to a
        # valid uuid4. This is bad for validation purposes.

        return str(val) == token


    def update_datetime(self):
        self.updated_at = datetime.utcnow()

    def __unicode__(self):
        return '<Session: {}>'.format(self.id)


__all__ = [
    'BaseSession',
]
