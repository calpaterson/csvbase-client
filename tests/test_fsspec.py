import fsspec
import pandas as pd

from pandas.testing import assert_frame_equal

from .utils import random_string, mock_auth


def test_open(test_user, http_sesh):
    fs = fsspec.filesystem("csvbase")

    table_name = random_string(prefix="table-")
    initial_df = pd.DataFrame({"string": ["Hello, {n}" for n in range(10)]})

    with mock_auth(test_user.username, test_user.hex_api_key()):
        with fs.open(f"{test_user.username}/{table_name}", "w") as table_f:
            initial_df.to_csv(table_f, index=False)

        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            actual_df = pd.read_csv(table_f, index_col=0)

    expected_df = initial_df.assign(csvbase_row_id=range(1, 11)).set_index(
        "csvbase_row_id"
    )

    assert_frame_equal(expected_df, actual_df)
