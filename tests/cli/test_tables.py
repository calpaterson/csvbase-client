"""Test getting and setting tables"""

from csvbase_client.internals.cli import cli

from .utils import mock_auth


def test_table__get(runner, test_user, test_table):
    """Test getting a table."""
    with mock_auth(test_user.username, test_user.hex_api_key()):
        result = runner.invoke(cli, ["table", "get", test_table])
    assert result.exit_code == 0, result.stderr_bytes
