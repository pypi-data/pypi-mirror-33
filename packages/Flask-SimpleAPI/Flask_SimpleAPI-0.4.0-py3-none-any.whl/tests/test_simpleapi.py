import pytest
from flask import json

from . import user
from flask_simpleapi import SimpleApi


@pytest.fixture
def client():
    app = SimpleApi(__name__)
    app.register_api(user)

    client = app.test_client()
    yield client


def test_url_without_param(client):
    res = client.get('/user/index')

    assert res.mimetype == 'application/json'
    assert json.loads(res.data)['hello'] == 'User'


def test_url_with_param(client):
    res = client.get('/user/info/mrbean')

    assert res.mimetype == 'application/json'
    assert json.loads(res.data)['hello'] == 'mrbean'
