import pytest
import fsspec
import dask.dataframe as dd
from pandas.testing import assert_frame_equal

from ..utils import random_dataframe, random_string, mock_auth


def random_dask_dataframe():
    return dd.from_pandas(random_dataframe())


def create_table(user, table_name: str, df: dd.DataFrame) -> None:
    """Creates a random table, returning the reference"""
    fs = fsspec.filesystem("csvbase")
    with mock_auth(user.username, user.hex_api_key()):
        with fs.open(f"{user.username}/{table_name}?public=true", "wb") as table_f:
            # dask doesn't have a way to write to a buffer, so go via pandas
            df.compute().to_csv(table_f, index=False)


@pytest.mark.xfail(reason="seems to require CSVBaseFileSystem to be thread safe")
def test_dask__read_happy(test_user):
    original_df = random_dask_dataframe()
    table_name = random_string()
    create_table(test_user, table_name, original_df)

    expected_df = original_df.set_index("A").compute()
    actual_df = dd.read_csv(f"csvbase://{test_user.username}/{table_name}").set_index(
        "A"
    )
    assert_frame_equal(expected_df.compute(), actual_df.compute())
