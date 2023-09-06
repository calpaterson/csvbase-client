from unittest.mock import patch
import random, string, contextlib

from csvbase_client.internals.value_objs import Auth
from csvbase_client.internals import auth as auth_module


def random_string(prefix: str = "", n: int = 32) -> str:
    return prefix + "".join(random.choice(string.ascii_lowercase) for _ in range(n))


@contextlib.contextmanager
def mock_auth(username: str, hex_api_key: str):
    auth = Auth(username, hex_api_key)
    with patch.object(auth_module, "_get_auth", return_value=auth):
        yield
