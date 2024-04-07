from unittest.mock import patch
import random
import string
import contextlib

import pandas as pd
import numpy as np

from csvbase_client.internals.value_objs import Auth
from csvbase_client.internals import auth as auth_module


def random_string(prefix: str = "", n: int = 32) -> str:
    return prefix + "".join(random.choice(string.ascii_lowercase) for _ in range(n))


@contextlib.contextmanager
def mock_auth(username: str, hex_api_key: str):
    auth = Auth(username, hex_api_key)
    with patch.object(auth_module, "_get_auth", return_value=auth):
        yield


def random_dataframe(row_count=100) -> pd.DataFrame:
    rng = np.random.default_rng()
    df = pd.DataFrame(rng.integers(0, 100, size=(row_count, 4)), columns=list("ABCD"))
    return df
