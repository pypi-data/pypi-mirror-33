import importlib
from _md5 import md5
from uuid import uuid4

from flask import current_app
from mongoengine import StringField, UUIDField, EmailField, ListField
from ..models import get_user_model
from ..core.model import TimestampedModel
from ..core.tools import my_import


class BaseUser(TimestampedModel):
    id = UUIDField(primary_key=True, default=uuid4)
    name = StringField()
    email = EmailField(unique=True)
    encrypted_password = StringField()
    perms = ListField(StringField(), null=True)

    meta = {
        'abstract': True
    }

    @staticmethod
    def authenticate(email, password):
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if not user.verify_password(password):
            return False

        return user

    @staticmethod
    def encrypt_password(password):
        salt = current_app.config['SECRET_KEY']
        h = md5('{}{}'.format(password, salt).encode('utf8'))
        return h.hexdigest()

    @classmethod
    def create(cls, name, email, password):
        enc_pass = cls.encrypt_password(password)
        return cls(name=name, email=email, encrypted_password=enc_pass).save()

    def has_perm(self, perm):
        return perm in self.perms

    def add_perm(self, perm):
        return self.update(push__perms=perm).reload()

    def remove_perm(self, perm):
        return self.update(pull__perms=perm).reload()

    def verify_password(self, password):
        return self.encrypt_password(password) == self.encrypted_password

    def __str__(self):
        return '<User: {}>'.format(self.email)


__all__ = [
    'BaseUser'
]
