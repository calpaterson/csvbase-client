from pathlib import Path
from io import BytesIO

from csvbase_client.constants import CSVBASE_DOT_COM
from csvbase_client.internals.cache import get_fs_cache, RepKey
from csvbase_client.internals.value_objs import ContentType
from csvbase_client.io import rewind


def test_fs_cache__getting_and_setting(tmpdir):
    cache = get_fs_cache(Path(str(tmpdir)))
    # FIXME: should include etag
    key = RepKey(CSVBASE_DOT_COM, "test/test", ContentType.CSV)
    filelike = BytesIO(b"rhubarb")

    # unset
    assert cache.get(key) is None

    # now set
    with rewind(filelike):
        cache.set(key, filelike)

    # check file is present where expected

    # assert that i can get it
    actual = cache.get(key)
    assert cache.get(key).read() == filelike.read()
