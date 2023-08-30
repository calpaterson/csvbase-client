import importlib.resources as imp_resources

import csvbase_client


def get_version() -> str:
    try:
        return get_softcoded_version()
    # These two are raised (under different scenarios) under Nuitka when trying
    # to import importlib.resources.files
    except (AttributeError, FileNotFoundError):
        return get_hardcoded_version()


def get_softcoded_version() -> str:
    """Return the version out of package metadata.

    This only works if we're in a valid package, with the valid package data.

    """
    # this isn't there in 3.8, which gets mypy confused (but we are using a
    # backport)
    version_path = imp_resources.files(csvbase_client) / "VERSION"  # type: ignore
    return version_path.open().read().strip()


def get_hardcoded_version() -> str:
    """Return the hardcoded version number.

    This is used when we're not in a valid package, for example when built by Nuitka.

    """
    return "0.0.1"
