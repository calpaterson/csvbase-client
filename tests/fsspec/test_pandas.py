import fsspec
import pandas as pd
from pandas.testing import assert_frame_equal

from ..utils import random_dataframe, random_string, mock_auth


def create_table(user, table_name: str, df: pd.DataFrame) -> None:
    """Creates a random table, returning the reference"""
    fs = fsspec.filesystem("csvbase")
    with mock_auth(user.username, user.hex_api_key()):
        with fs.open(f"{user.username}/{table_name}?public=true", "wb") as table_f:
            df.to_csv(table_f, index=False)


def test_pandas__read_happy(test_user, flask_adapter):
    """Read a CSV via pd.read_csv(csvbase://[...])"""
    original_df = random_dataframe()
    table_name = random_string()
    create_table(test_user, table_name, original_df)

    actual_df = pd.read_csv(
        f"csvbase://{test_user.username}/{table_name}", index_col=0
    ).set_index("A")
    expected_df = original_df.set_index("A")
    assert_frame_equal(expected_df, actual_df)
