import io
from typing import Dict, Optional, IO
import shutil
from logging import getLogger
from urllib.parse import urljoin

import requests
from pyappcache.keys import Key
from pyappcache.fs import FilesystemCache
from fsspec.spec import AbstractFileSystem, AbstractBufferedFile

from .io import rewind
from .internals.cache import get_fs_cache, get_last_etag, set_etag, RepKey
from .internals.value_objs import Auth, ContentType
from .internals.auth import get_auth
from .internals.http import get_http_sesh, HTTP_TIMEOUT
from .constants import CSVBASE_DOT_COM
from .exceptions import http_error_to_user_message, CSVBaseException

logger = getLogger(__name__)


def get_rep(
    http_sesh: requests.Session,
    cache: FilesystemCache,
    base_url: str,
    ref: str,
    content_type: ContentType,
    auth: Optional[Auth] = None,
) -> IO[bytes]:
    headers = {"Accept": "text/csv"}
    if auth is not None:
        headers["Authorization"] = auth.as_basic_auth()
    # breakpoint()
    url = url_for_rep(base_url, ref, content_type)
    etag = get_last_etag(cache, base_url, ref, content_type)
    rep_key: Key[IO[bytes]] = RepKey(base_url, ref, content_type)

    if etag is not None:
        rep = cache.get(rep_key)
        if rep is not None:
            logger.debug("last known etag found: '%s' ('%s')", ref, etag)
            headers["If-None-Match"] = etag
        else:
            logger.debug("an etag is known but cache MISS: '%s'", ref)
    else:
        logger.debug("no etag known")

    response = http_sesh.get(url, headers=headers, stream=True, timeout=HTTP_TIMEOUT)
    logger.info("got response code: %d", response.status_code)

    # make sure to log all 500s to make it clear a real error has occurred
    if response.status_code >= 500:
        logger.error("got status_code: %d, %s", response.status_code, response.content)

    # 400s and 500s are raised as exceptions
    if response.status_code >= 400:
        message = http_error_to_user_message(ref, response)
        raise CSVBaseException(message)

    if response.status_code == 304:
        # FIXME: a rejig is required here for type safety
        return rep  # type: ignore
    else:
        etag = response.headers["ETag"]
        set_etag(cache, base_url, ref, content_type, etag)
        rep = io.BytesIO()
        with rewind(rep):
            shutil.copyfileobj(response.raw, rep)
            response.close()
        with rewind(rep):
            cache.set(rep_key, rep)

    return rep


def send_rep(
    http_sesh: requests.Session,
    cache: FilesystemCache,
    base_url: str,
    ref: str,
    content_type: ContentType,
    rep: IO[bytes],
    auth: Optional[Auth] = None,
) -> None:
    headers = {"Content-Type": content_type.mimetype()}
    if auth is not None:
        headers["Authorization"] = auth.as_basic_auth()
    url = url_for_rep(base_url, ref, content_type)
    response = http_sesh.put(url, data=rep, headers=headers, timeout=HTTP_TIMEOUT)
    response.raise_for_status()


def url_for_rep(base_url: str, ref: str, content_type: ContentType) -> str:
    url = urljoin(base_url, ref)
    return url


class CSVBaseFileSystem(AbstractFileSystem):
    def __init__(self, *args, **kwargs):
        kwargs["use_listings_cache"] = False
        self._base_url = CSVBASE_DOT_COM
        self._cache = get_fs_cache()

        super().__init__(*args, **kwargs)

    def fsid(self):
        raise NotImplementedError

    def _open(
        self,
        path,
        mode="rb",
        block_size=None,
        autocommit=True,
        cache_options=None,
        **kwargs
    ):
        f = CSVBaseFile(self, path, mode)
        return f

    def created(self, path):
        raise NotImplementedError

    def modified(self, path):
        raise NotImplementedError

    def cp_file(self, path1, path2, **kwargs):
        raise NotImplementedError

    def touch(self, path, truncate=True, **kwargs):
        # This will never be implemented
        raise NotImplementedError

    def ls(self, path, detail: bool = True):
        # FIXME: need a way to list a users' tables
        return []

    def _rm(self, path):
        raise NotImplementedError

    def info(self, path: str) -> Dict:
        return {
            "name": path,
            "size": None,
            "type": "file" if "/" in path else "directory",
        }

    def _get_rep(self, ref: str, content_type: ContentType) -> IO[bytes]:
        _http_sesh = get_http_sesh()
        return get_rep(
            _http_sesh,
            self._cache,
            self._base_url,
            ref,
            content_type,
            self._get_auth(),
        )

    def _send_rep(self, ref: str, content_type: ContentType, rep: IO[bytes]) -> None:
        _http_sesh = get_http_sesh()
        send_rep(
            _http_sesh,
            self._cache,
            self._base_url,
            ref,
            content_type,
            rep,
            self._get_auth(),
        )

    def _get_auth(self) -> Optional[Auth]:
        # this can't be done on an instance level for testing reasons - fsspec
        # appears to re-use instances
        return get_auth()


class CSVBaseFile(AbstractBufferedFile):
    def __init__(self, fs: CSVBaseFileSystem, path, mode, **kwargs) -> None:
        self.fs = fs
        self.path = path
        self._staging_buffer = io.BytesIO()
        # this is necessary because we have no way to get size of the file
        if mode == "rb":
            with rewind(self._staging_buffer):
                shutil.copyfileobj(
                    fs._get_rep(path, ContentType.CSV), self._staging_buffer
                )
                size = self._staging_buffer.tell()
        else:
            size = 0

        # currently this value is used only for test multi-chunk uploads
        self._chunk_count = 0

        super().__init__(fs, path, mode, size=size, cache_type="none", **kwargs)

    def _fetch_range(self, start: int, end: int) -> bytes:
        self._staging_buffer.seek(start)
        count = end - start
        return self._staging_buffer.read(count)

    def _initiate_upload(self) -> None:
        # FIXME: possibly truncate the staging buffer
        pass

    def _upload_chunk(self, final=False) -> None:
        # we send it all in one go at the moment
        self.buffer.seek(0)
        shutil.copyfileobj(self.buffer, self._staging_buffer)
        self._chunk_count += 1
        if final:
            self._staging_buffer.seek(0)
            self.fs._send_rep(self.path, ContentType.CSV, self._staging_buffer)
