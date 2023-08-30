import os
from unittest.mock import patch


from csvbase_client.internals.auth import get_auth


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
