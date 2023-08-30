"""Test getting and setting tables"""

from io import BytesIO

import pandas as pd
from pandas.testing import assert_frame_equal

from csvbase_client.internals.cli import cli

from .utils import mock_auth, random_string


def test_get__happy(runner, test_user, test_table):
    """Test getting a table."""
    with mock_auth(test_user.username, test_user.hex_api_key()):
        result = runner.invoke(cli, ["table", "get", test_table])
    assert result.exit_code == 0, result.stderr_bytes


def test_set__to_create(runner, test_user, tmpdir):
    """Test setting a table."""
    table_name = random_string()
    table_filepath = str(tmpdir / f"{table_name}.csv")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    df.to_csv(table_filepath, index=False)

    ref = "/".join([test_user.username, table_name])

    with mock_auth(test_user.username, test_user.hex_api_key()):
        # set the table
        result = runner.invoke(cli, ["table", "set", ref, table_filepath])
        assert result.exit_code == 0, result.stderr_bytes

        # get it back and compare
        result = runner.invoke(cli, ["table", "get", ref])
        assert result.exit_code == 0, result.stderr_bytes
        actual_df = pd.read_csv(BytesIO(result.stdout_bytes)).drop(
            columns="csvbase_row_id"
        )

        assert_frame_equal(df, actual_df)
