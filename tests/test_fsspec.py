import fsspec
import pandas as pd

import pytest

from pandas.testing import assert_frame_equal

from .utils import random_string, mock_auth


def test_open__happy(test_user, http_sesh):
    table_name = random_string(prefix="table-")
    initial_df = pd.DataFrame({"string": ["Hello, {n}" for n in range(10)]})

    with mock_auth(test_user.username, test_user.hex_api_key()):
        print(test_user)
        fs = fsspec.filesystem("csvbase")

        # upload a table
        with fs.open(f"{test_user.username}/{table_name}", "w") as table_f:
            initial_df.to_csv(table_f, index=False)

        # download a table
        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            actual_df = pd.read_csv(table_f, index_col=0)

    expected_df = initial_df.assign(csvbase_row_id=range(1, 11)).set_index(
        "csvbase_row_id"
    )

    assert_frame_equal(expected_df, actual_df)


def test_open__cache_hit(test_user, http_sesh, flask_adapter):
    table_name = random_string(prefix="table-")
    initial_df = pd.DataFrame({"string": ["Hello, {n}" for n in range(10)]})

    with mock_auth(test_user.username, test_user.hex_api_key()):
        print(test_user)
        fs = fsspec.filesystem("csvbase")

        with fs.open(f"{test_user.username}/{table_name}", "w") as table_f:
            initial_df.to_csv(table_f, index=False)

        # cache filling request
        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            table_f.read()

        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            actual_df = pd.read_csv(table_f, index_col=0)

    expected_df = initial_df.assign(csvbase_row_id=range(1, 11)).set_index(
        "csvbase_row_id"
    )

    # FIXME: this doesn't assert that the cache was used
    assert_frame_equal(expected_df, actual_df)
    third_req, third_resp = flask_adapter.request_response_pairs[2]
    "Etag" in third_req.headers
    third_resp.status_code == 304
