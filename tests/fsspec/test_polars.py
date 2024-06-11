import polars as pl

import fsspec
from polars.testing import assert_frame_equal

import pytest
from ..utils import random_dataframe, random_string, mock_auth


def random_polars_dataframe():
    return pl.from_pandas(random_dataframe())


def create_table(user, table_name: str, df: pl.DataFrame) -> None:
    """Creates a random table, returning the reference"""
    fs = fsspec.filesystem("csvbase")
    with mock_auth(user.username, user.hex_api_key()):
        with fs.open(f"{user.username}/{table_name}?public=true", "wb") as table_f:
            df.write_csv(table_f)


def test_polars__read_happy_csv(test_user, flask_adapter):
    """Read a CSV via pl.read_csv(csvbase://[...])"""
    original_df = random_polars_dataframe()
    table_name = random_string()
    create_table(test_user, table_name, original_df)

    actual_df = pl.read_csv(f"csvbase://{test_user.username}/{table_name}").drop(
        "csvbase_row_id"
    )
    expected_df = original_df
    assert_frame_equal(expected_df, actual_df)


@pytest.mark.xfail(
    reason="polars bug: https://github.com/pola-rs/polars/issues/16737", strict=True
)
def test_polars__read_happy_parquet(test_user, flask_adapter):
    original_df = random_polars_dataframe()
    table_name = random_string()
    create_table(test_user, table_name, original_df)

    actual_df = pl.read_parquet(
        f"csvbase://{test_user.username}/{table_name}.parquet"
    ).drop("csvbase_row_id")
    expected_df = original_df
    assert_frame_equal(expected_df, actual_df)
