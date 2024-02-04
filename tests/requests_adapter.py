# Need to wait for a release of types-requests that includes this commit:
# https://github.com/python/typeshed/commit/b69b17c3d8fd5b1f0cc8209b2f15e6b4b687a2ee
# mypy: ignore-errors

from base64 import b64encode
from io import BytesIO

import requests
from requests.adapters import BaseAdapter


def basic_auth(username, password) -> str:
    user_pass = f"{username}:{password}".encode("utf-8")
    encoded = b64encode(user_pass).decode("utf-8")
    return f"Basic {encoded}"


class FlaskAdapter(BaseAdapter):
    """Adapts requests requests into requests against a flask app's test client."""

    def __init__(self, test_client):
        self.test_client = test_client
        self.request_response_pairs = []

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool,
        timeout,
        verify: bool,
        cert,
        proxies,
    ) -> requests.Response:
        flask_response = self.test_client.open(
            path=request.path_url,
            method=request.method,
            headers=dict(request.headers),
            data=request.body.read() if request.body is not None else None,
        )
        response = requests.Response()
        response.status_code = flask_response.status_code
        response.raw = BytesIO(flask_response.data)
        response.url = request.path_url
        response.reason = flask_response.status[4:]
        response.headers = flask_response.headers
        self.request_response_pairs.append((request, response))
        return response
