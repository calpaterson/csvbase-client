import re

from csvbase_client.internals.version import (
    get_version,
    get_softcoded_version,
    get_hardcoded_version,
)


def test_version_is_valid():
    VERSION_REGEX = re.compile(r"^\d+\.\d+\.\d+$")
    assert VERSION_REGEX.match(get_version())


def test_hardcoded_version_matches_softcoded():
    assert get_softcoded_version() == get_hardcoded_version()
