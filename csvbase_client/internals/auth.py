from logging import getLogger
from typing import Optional
from netrc import netrc

from .value_objs import Auth

logger = getLogger(__name__)


def _get_auth(host) -> Optional[Auth]:
    netrc_f = netrc()
    try:
        username, _, api_key = netrc_f.authenticators(host)
    except ValueError:
        logger.info("nothing found in netrc for host: %s", host)
        return None
    logger.info("using api-key for %s, found in netrc", username)
    return Auth(username, api_key)


def get_auth(host: str = "csvbase.com") -> Optional[Auth]:
    return _get_auth(host)
