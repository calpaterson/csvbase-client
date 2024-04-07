import fsspec
import pandas as pd
import pytest
import io
from typing import IO
import os
from pandas.testing import assert_frame_equal

from csvbase_client.exceptions import CSVBaseException

from csvbase_client.io import rewind
from .utils import random_string, mock_auth, random_dataframe


def test_open__happy(test_user, http_sesh):
    table_name = random_string(prefix="table-")
    initial_df = pd.DataFrame({"string": [f"Hello, {n}" for n in range(10)]})

    with mock_auth(test_user.username, test_user.hex_api_key()):
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
    initial_df = pd.DataFrame({"string": [f"Hello, {n}" for n in range(10)]})

    with mock_auth(test_user.username, test_user.hex_api_key()):
        fs = fsspec.filesystem("csvbase")

        with fs.open(f"{test_user.username}/{table_name}", "w") as table_f:
            initial_df.to_csv(table_f, index=False)

        # cache filling request
        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            table_f.read()

        # cache hit request
        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            actual_df = pd.read_csv(table_f, index_col=0)

    expected_df = initial_df.assign(csvbase_row_id=range(1, 11)).set_index(
        "csvbase_row_id"
    )

    # check that the data is as expected
    assert_frame_equal(expected_df, actual_df)

    # check that a cache was used
    second_req, second_resp = flask_adapter.request_response_pairs[1]
    third_req, third_resp = flask_adapter.request_response_pairs[2]
    etag = second_resp.headers["ETag"]
    assert third_req.headers["If-None-Match"] == etag
    assert "ETag" not in third_resp
    third_resp.status_code == 304

    # check that the layout of the cache is as expected
    cache_path = fs._cache.directory / f"v0_{test_user.username}_{table_name}.csv"
    assert cache_path.exists()
    cached_df = pd.read_csv(cache_path, index_col=0)
    assert_frame_equal(expected_df, cached_df)


def test_open__does_not_exist(test_user, http_sesh, flask_adapter):
    fs = fsspec.filesystem("csvbase")
    table_name = random_string(prefix="table-")
    with pytest.raises(CSVBaseException):
        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            pd.read_csv(table_f.read())


def test_csvbase_file__upload_multi_chunk(test_user, http_sesh, flask_adapter):
    """Check that larger uploads (which are done via multiple calls to
    _upload_chunk send the whole file.

    Note that fsspec uses the terms "block" and "chunk" somewhat interchangeably.

    """
    table_name = random_string(prefix="table-")
    df = random_dataframe()
    table_buf = io.BytesIO()
    with rewind(table_buf):
        df.to_csv(table_buf, index=False)
    buf_size = _get_fh_size(table_buf)
    chunk_size = buf_size // 4

    with mock_auth(test_user.username, test_user.hex_api_key()):
        fs = fsspec.filesystem("csvbase")

        with fs.open(f"{test_user.username}/{table_name}", mode="wb") as table_f:
            # make the blocksize artificially low to exercise this
            # functionality
            table_f.blocksize = chunk_size

            while len(chunk := table_buf.read(chunk_size)) > 0:
                table_f.write(chunk)
            assert table_f._chunk_count == 4, "not a multi-chunk upload"

        with fs.open(f"{test_user.username}/{table_name}") as table_f:
            actual_df = pd.read_csv(table_f).drop(columns="csvbase_row_id")

    assert_frame_equal(df, actual_df)


# FIXME: this should be somewhere else.  Probably in pyappcache.
def _get_fh_size(fh: IO[bytes]) -> int:
    """Return the size of a seekable binary filehandle."""
    pos = fh.tell()
    fh.seek(0, os.SEEK_END)
    size = fh.tell()
    fh.seek(pos)
    return size
