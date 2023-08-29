from urllib.parse import urljoin
import requests

from .value_objs import ContentType


def _get_http_sesh() -> requests.Session:
    """This internal function exists only for testing/mocking reasons."""
    return requests.Session()


def get_http_sesh() -> requests.Session:
    sesh = _get_http_sesh()
    # disable automatic loading from the netrc - we will do that (so that we
    # can log it)
    sesh.trust_env = False
    version = "0.0.1"  # FIXME:
    sesh.headers.update({"User-Agent": f"csvbase-client/{version}"})
    return sesh


def ref_to_url(base_url: str, ref: str, content_type: ContentType) -> str:
    url = urljoin(base_url, ref)
    if content_type is not None:
        url += content_type.file_extension()
    return url
