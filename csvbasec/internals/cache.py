import sqlite3
from contextlib import closing
from logging import getLogger
from pathlib import Path
from typing import List, Optional

import requests
from pyappcache.keys import BaseKey, Key
from pyappcache.sqlite_lru import SqliteCache

from .dirs import dirs

logger = getLogger(__name__)

HTTP_TIMEOUTS = (1, 30)

ETAGS_DDL = """
CREATE TABLE IF NOT EXISTS etags (
    ref text PRIMARY KEY,
    etag text NOT NULL
);
"""

GET_ETAG_DML = """
SELECT
    etag
FROM
    etags
WHERE
    ref = ?
"""

SET_ETAG_DML = """
INSERT
    OR REPLACE INTO etags (ref, etag)
        VALUES (?, ?);
"""


class ETagKey(BaseKey):
    def __init__(self, ref):
        self.ref = ref

    def cache_key_segments(self) -> List[str]:
        return [self.ref]  # FIXME: correct this in the docs


class TableCache:
    """A read-through cache of tables."""

    def __init__(self) -> None:
        cache_db_path = Path(dirs.user_cache_dir) / "cache.db"
        logger.info("cache db path = %s", cache_db_path)
        cache_db_path.parent.mkdir(parents=True, exist_ok=True)
        self._sqlite_conn = sqlite3.connect(cache_db_path)
        self._create_etags_table()
        self._lru_cache = SqliteCache(max_size=100, connection=self._sqlite_conn)
        self._http_client = requests.Session()
        version = "0.0.1"  # FIXME:
        self._http_client.headers.update({"User-Agent": f"cbc/{version}"})

    def get_table(self, ref: str) -> str:
        headers = {"Accept": "text/csv"}
        etag = self._get_etag(ref)
        if etag is not None:
            logger.debug("etag found: %s", etag)
            key: Key[str] = ETagKey(etag)
            table = self._lru_cache.get(key)
            if table is not None:
                logger.debug("cache HIT: %s", ref)
                headers["If-None-Match"] = etag
            else:
                logger.debug("etag known but cache MISS: %s", ref)

        response = self._http_client.get(
            self._build_url_for_table_ref(ref),
            headers=headers,
        )

        # FIXME: handle these errors
        response.raise_for_status()

        if response.status_code == 304:
            logger.debug("server says cache still valid")
            return table
        else:
            received_etag = response.headers["ETag"]
            received_etag_key: Key[str] = ETagKey(received_etag)
            table = response.text
            self._set_etag(ref, received_etag)
            self._lru_cache.set(received_etag_key, response.text)
            return table

    def _build_url_for_table_ref(self, ref: str) -> str:
        return f"https://csvbase.com/{ref}"

    def _get_etag(self, ref: str) -> Optional[str]:
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(GET_ETAG_DML, (ref,))
            rs = cursor.fetchone()
        if rs is not None:
            return rs[0]
        else:
            return None

    def _set_etag(self, ref: str, etag: str) -> None:
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(SET_ETAG_DML, (ref, etag))
            self._sqlite_conn.commit()

    def _create_etags_table(self):
        with closing(self._sqlite_conn.cursor()) as cursor:
            cursor.execute(ETAGS_DDL)
            self._sqlite_conn.commit()
