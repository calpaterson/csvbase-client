from io import BytesIO

from requests.auth import HTTPBasicAuth
import pandas as pd
from csvbase.streams import rewind
from click.testing import CliRunner
import pytest

from ..utils import random_string
from .utils import format_response_error


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture()
def test_table(test_user, http_sesh) -> str:
    table_name = random_string(prefix="cli-test-table-", n=10)
    df = pd.DataFrame({"a": [1, 2, 3]})
    buf = BytesIO()
    with rewind(buf):
        df.to_csv(buf)
    resp = http_sesh.put(
        f"https://csvbase.com/{test_user.username}/{table_name}",
        data=buf,
        headers={"Content-Type": "text/csv"},
        auth=HTTPBasicAuth(test_user.username, test_user.hex_api_key()),
    )
    assert resp.status_code == 201, format_response_error(resp)
    return "/".join([test_user.username, table_name])
