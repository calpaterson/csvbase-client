import sqlite3
import shutil
from contextlib import closing
from logging import getLogger
from pathlib import Path
from typing import List, Optional, IO, Any, Dict, Iterable, Tuple
from io import BytesIO
from urllib.parse import urljoin
from datetime import datetime, timezone

from pyappcache.keys import BaseKey, Key
from pyappcache.sqlite_lru import SqliteCache
from pyappcache.serialisation import Serialiser

from .config import Config
from .http import get_http_sesh
from .dirs import dirs
from .value_objs import Auth, ContentType

logger = getLogger(__name__)

HTTP_TIMEOUTS = (5, 60)

ETAGS_DDL = """
CREATE TABLE IF NOT EXISTS etags (
    ref text,
    etag text NOT NULL,
    content_type text NOT NULL,
    last_modified text NOT NULL,
    PRIMARY KEY (ref, content_type)
);
"""

GET_ETAG_DQL = """
SELECT
    etag
FROM
    etags
WHERE
    ref = ?
AND
    content_type = ?
"""

#
SET_ETAG_DML = """
INSERT INTO etags (ref, etag, content_type, last_modified)
VALUES (?, ?, ?, ?)
ON CONFLICT(ref, content_type) DO UPDATE SET
    etag = excluded.etag,
    last_modified = excluded.last_modified;

"""

GET_CACHE_INFO_DQL = """
SELECT
   ref, etag, content_type, last_modified
FROM etags
JOIN
   pyappcache
ON key = 'pyappcache/' || etag
"""


class ETagKey(BaseKey):
    def __init__(self, ref):
        self.ref = ref

    def cache_key_segments(self) -> List[str]:
        return [self.ref]  # FIXME: correct this in the docs

    def should_compress(self, python_obj, as_bytes) -> bool:
        # csv files are highly compressible
        return True


def cache_path() -> Path:
    return Path(dirs.user_cache_dir) / "cache.db"


class TableCache:
    """A read-through cache of tables."""

    def __init__(self, config: Config) -> None:
        cache_db_path = cache_path()
        logger.info("cache db path = %s", cache_db_path)
        cache_db_path.parent.mkdir(parents=True, exist_ok=True)
        self._sqlite_conn = sqlite3.connect(cache_db_path)
        self._create_etags_table()
        self._lru_cache = SqliteCache(max_size=100, connection=self._sqlite_conn)
        self._lru_cache.prefix = (
            "pyappcache"  # FIXME: necessary because of a bug upstream
        )
        self._http_client = get_http_sesh()

    def base_url(self) -> str:
        return "https://csvbase.com/"

    def check_creds(self, config: Config) -> bool:
        if config.username is None or config.api_key is None:
            return False
        response = self._http_client.get(urljoin(self.base_url(), config.username))
        if 400 <= response.status_code < 500:
            return False
        elif 200 <= response.status_code < 300:
            return True
        else:
            response.raise_for_status()
            # this (should be) unreachable but typechecker doesn't know that
            return False

    def get_table(
        self, ref: str, auth: Optional[Auth] = None, force_miss: bool = False
    ) -> IO[bytes]:
        content_type = ContentType.CSV
        headers = {"Accept": content_type.mimetype()}
        if auth is not None:
            headers["Authorization"] = auth.as_basic_auth()
        url = self._build_url_for_table_ref(ref, content_type)
        canon_url = self._build_url_for_table_ref(ref)
        etag = self._get_etag(canon_url)
        if etag is not None:
            logger.debug("etag found: %s", etag)
            key: Key[IO[bytes]] = ETagKey(etag)
            table = self._lru_cache.get(key)
            if table is not None:
                logger.debug("cache HIT: %s", ref)
                if force_miss:
                    logger.info("cache HIT but forcing MISS")
                else:
                    headers["If-None-Match"] = etag
            else:
                logger.debug("etag known but cache MISS: %s", ref)

        response = self._http_client.get(url, headers=headers, stream=True)

        if response.status_code >= 400:
            logger.error(
                "got status_code: %d, %s", response.status_code, response.content
            )

            response.raise_for_status()

        if response.status_code == 304:
            logger.debug("server says cache still valid")
            # typechecker thinks this is still optional but it can't be if we
            # got here
            return table  # type: ignore
        else:
            received_etag = response.headers["ETag"]
            received_etag_key = ETagKey(received_etag)
            self._set_etag(canon_url, received_etag, ContentType.CSV)
            buf: BytesIO = BytesIO()
            shutil.copyfileobj(response.raw, buf)
            response.close()
            buf.seek(0)
            self._lru_cache.set(received_etag_key, buf)
            buf.seek(0)
            return buf

    def metadata(self, ref: str) -> Dict[str, Any]:
        headers = {"Accept": "application/json"}
        response = self._http_client.get(
            self._build_url_for_table_ref(ref), headers=headers
        )

        response.raise_for_status()
        rv = {"etag": response.headers["ETag"]}
        rv.update(response.json())
        return rv

    def set_table(
        self, ref: str, file_obj: IO[str], auth: Optional[Auth] = None
    ) -> None:
        headers = {"Content-Type": "text/csv"}
        if auth is not None:
            headers["Authorization"] = auth.as_basic_auth()
        url = self._build_url_for_table_ref(ref)
        response = self._http_client.put(url, data=file_obj, headers=headers)
        response.raise_for_status()

    def _build_url_for_table_ref(
        self, ref: str, content_type: Optional[ContentType] = None
    ) -> str:
        url = urljoin(self.base_url(), ref)
        if content_type is not None:
            url += content_type.file_extension()
        return url

    def _get_etag(self, ref: str) -> Optional[str]:
        # FIXME: This still isn't quite right as etags need to take account of
        # Vary, but we aren't.
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(GET_ETAG_DQL, (ref, "text/csv"))
            rs = cursor.fetchone()
        if rs is not None:
            return rs[0]
        else:
            return None

    def _set_etag(self, url: str, etag: str, content_type: ContentType) -> None:
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(
                SET_ETAG_DML,
                (
                    url,
                    etag,
                    content_type.mimetype(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self._sqlite_conn.commit()

    def _create_etags_table(self):
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(ETAGS_DDL)
            self._sqlite_conn.commit()

    def entries(self) -> Iterable[Tuple[str, str, ContentType, datetime]]:
        def parse_row(
            url, etag, content_type_str, last_modified_str
        ) -> Tuple[str, str, ContentType, datetime]:
            content_type = ContentType.from_mimetype(content_type_str)
            last_modified = datetime.fromisoformat(last_modified_str)
            return (url, etag, content_type, last_modified)

        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(GET_CACHE_INFO_DQL)
            yield from (parse_row(*row) for row in cursor)

    def clear(self) -> None:
        if cache_path().exists():
            cache_path().unlink()


class StreamSerialiser(Serialiser):
    def dump(self, obj: Any) -> IO[bytes]:
        return obj

    def load(self, data: IO[bytes]) -> Any:
        return data
