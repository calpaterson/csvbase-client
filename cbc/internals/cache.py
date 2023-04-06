import sqlite3
import shutil
from contextlib import closing
from logging import getLogger
from pathlib import Path
from typing import List, Optional, IO, Any
from io import BytesIO

import requests
from pyappcache.keys import BaseKey, Key
from pyappcache.sqlite_lru import SqliteCache
from pyappcache.serialisation import Serialiser

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

    def should_compress(self, python_obj, as_bytes) -> bool:
        # csv files are highly compressible
        return True


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

    def get_table(self, ref: str, force_miss: bool = False) -> IO[bytes]:
        headers = {"Accept": "text/csv"}
        etag = self._get_etag(ref)
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

        response = self._http_client.get(
            self._build_url_for_table_ref(ref), headers=headers, stream=True
        )

        # FIXME: handle these errors
        response.raise_for_status()

        if response.status_code == 304:
            logger.debug("server says cache still valid")
            # typechecker thinks this is still optional but it can't be if we
            # got here
            return table  # type: ignore
        else:
            received_etag = response.headers["ETag"]
            received_etag_key = ETagKey(received_etag)
            self._set_etag(ref, received_etag)
            buf: BytesIO = BytesIO()
            shutil.copyfileobj(response.raw, buf)
            response.close()
            buf.seek(0)
            self._lru_cache.set(received_etag_key, buf)
            buf.seek(0)
            return buf

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


class StreamSerialiser(Serialiser):
    def dump(self, obj: Any) -> IO[bytes]:
        return obj

    def load(self, data: IO[bytes]) -> Any:
        return data
