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
            data=request.body.getvalue() if request.body is not None else None,
        )
        response = requests.Response()
        response.status_code = flask_response.status_code
        response.raw = BytesIO(flask_response.data)
        response.url = request.path_url
        response.reason = flask_response.status[4:]
        response.headers = flask_response.headers
        return response
