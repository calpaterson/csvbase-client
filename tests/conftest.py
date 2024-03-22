from unittest.mock import patch

import requests
from csvbase.config import get_config
from csvbase.svc import create_user
from csvbase.web.app import init_app
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pytest

from csvbase_client.internals import http

from .utils import random_string
from .value_objs import ExtendedUser
from .requests_adapter import FlaskAdapter


@pytest.fixture(scope="session")
def db_engine():
    db_url = get_config().db_url
    return create_engine(db_url)


@pytest.fixture(scope="function")
def db_sesh(db_engine):
    with Session(db_engine) as db_sesh:
        yield db_sesh


@pytest.fixture()
def test_user(db_sesh):
    """Create a user.

    There is not (and probably never will be) a way to create a user via the
    API, so call directly into svc to do this.

    """
    crypt_context = CryptContext(["plaintext"])
    username = random_string(prefix="cli-test-user-", n=20)
    password = "password"
    user = create_user(db_sesh, crypt_context, username, password)
    db_sesh.commit()
    return ExtendedUser(
        username=username,
        user_uuid=user.user_uuid,
        password=password,
        registered=user.registered,
        api_key=user.api_key,
        email=user.email,
        timezone=user.timezone,
    )


@pytest.fixture(scope="session")
def csvbase_flask_app():
    app = init_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    return app


@pytest.fixture()
def csvbase_test_client(csvbase_flask_app):
    with csvbase_flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def flask_adapter(csvbase_test_client):
    return FlaskAdapter(csvbase_test_client)


@pytest.fixture(autouse=True)
def http_sesh(flask_adapter):
    """This fixture inserts our special requests->flask adapter."""
    sesh = requests.Session()
    sesh.mount("https://csvbase.com", flask_adapter)
    with patch.object(http, "_get_http_sesh") as mock_get_sesh:
        mock_get_sesh.return_value = sesh
        yield sesh
