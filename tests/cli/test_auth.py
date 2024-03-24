import os
from unittest.mock import patch


from csvbase_client.internals.auth import _get_auth


def get_auth(host="csvbase.com"):
    # this is to work around the default mocking of _get_auth - _get_auth is
    # import here prior to the mocking time
    return _get_auth(host)


def test_netrc(tmpdir):
    sample_netrc = """
machine csvbase.com
  login test
  password password
"""
    netrc = tmpdir / ".netrc"
    netrc.write(sample_netrc)
    netrc.chmod(0o600)
    with patch.dict(os.environ, {"HOME": str(tmpdir)}):
        auth = get_auth()
    assert auth.username == "test"
    assert auth.api_key == "password"


def test_netrc_absent(tmpdir):
    with patch.dict(os.environ, {"HOME": str(tmpdir)}):
        auth = get_auth()
    assert auth is None


def test_netrc_too_permissive(tmpdir):
    netrc = tmpdir / ".netrc"
    sample_netrc = """
machine csvbase.com
  login test
  password password
"""
    netrc = tmpdir / ".netrc"
    netrc.write(sample_netrc)
    with patch.dict(os.environ, {"HOME": str(tmpdir)}):
        auth = get_auth()
    assert auth is None
