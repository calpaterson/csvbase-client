from io import BytesIO

from csvbase_client.internals.cli import cli
from csvbase_client.internals.cache import get_fs_cache, RepKey
from csvbase_client.constants import CSVBASE_DOT_COM
from csvbase_client.internals.value_objs import ContentType


def test_cache_clear__removes_entries(runner):
    """Check that `csvbase-client cache clear` removes all entries"""
    key = RepKey(CSVBASE_DOT_COM, "test/test", ContentType.CSV)
    fs_cache = get_fs_cache()
    fs_cache.set(key, BytesIO(b"test"))

    # assert that that rep made it into the cache
    cache_dir = fs_cache.directory
    assert len(list(cache_dir.glob("*.csv"))) == 1

    result = runner.invoke(cli, ["cache", "clear"])
    assert result.exit_code == 0

    # assert that that entry is gone
    assert len(list(cache_dir.glob("*.csv"))) == 0


def test_cache__show_with_no_entries(runner):
    result = runner.invoke(cli, ["cache", "show"])
    assert result.exit_code == 0
