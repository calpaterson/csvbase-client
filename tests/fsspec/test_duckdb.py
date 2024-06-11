import duckdb
from pandas.testing import assert_frame_equal

from ..utils import random_dataframe, random_string, mock_auth


def random_duckdb_table():
    random_df = random_dataframe()
    table_name = random_string()
    duckdb.sql(f"CREATE TABLE {table_name} AS SELECT * FROM random_df")
    return table_name


def create_table(user, table_name: str):
    with mock_auth(user.username, user.hex_api_key()):
        duckdb.sql(
            f"COPY {table_name} TO 'csvbase://{user.username}/{table_name}?public=true' (HEADER, DELIMITER ',')"
        )


def test_duckdb__read_happy_csv(test_user, flask_adapter):
    original_table_name = random_duckdb_table()
    create_table(test_user, original_table_name)

    actual_table_name = random_string()
    duckdb.sql(
        f"CREATE TABLE {actual_table_name} AS FROM read_csv('csvbase://{test_user.username}/{original_table_name}')"
    )

    expected_df = duckdb.sql(f"select * from {original_table_name}").df()
    actual_df = (
        duckdb.sql(f"select * from {actual_table_name}")
        .df()
        .drop(columns="csvbase_row_id")
    )

    assert_frame_equal(expected_df, actual_df)
