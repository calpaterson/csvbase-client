import io
from typing import Dict
import shutil
from logging import getLogger

from fsspec.spec import AbstractFileSystem, AbstractBufferedFile

from .internals.auth import get_auth

logger = getLogger(__name__)


class CSVBaseFileSystem(AbstractFileSystem):
    def __init__(self, *args, **kwargs):
        kwargs["use_listings_cache"] = False
        super().__init__(*args, **kwargs)

    def fsid(self):
        raise NotImplementedError

    def _open(self, path, mode="rb", block_size = None, autocommit=True, cache_options=None, **kwargs):
        return CSVBaseFile(self, path, mode)

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


class CSVBaseFile(AbstractBufferedFile):
    def __init__(
        self, fs, path, mode, csvbase_base_url: str = "https://csvbase.com/", **kwargs
    ):
        self.path = path
        self.chunks = []
        self._staging_buffer = io.BytesIO()
        self.csvbase_base_url = csvbase_base_url
        self.csvbase_auth = get_auth()

        from csvbase_client.internals.cache import TableCache
        from csvbase_client.internals.config import get_config

        self._csvbase_cache = TableCache(get_config())
        if mode == "rb":
            shutil.copyfileobj(
                self._csvbase_cache.get_table(self.path, get_auth()),
                self._staging_buffer,
            )
            self._staging_buffer.seek(0, io.SEEK_END)
            size = self._staging_buffer.tell()
        else:
            size = None

        super().__init__(fs, path, mode, size=size, cache_type="none", **kwargs)

    def _upload_chunk(self, final=False) -> None:
        self.buffer.seek(0)
        shutil.copyfileobj(self.buffer, self._staging_buffer)
        if final:
            self._staging_buffer.seek(0)
            self._csvbase_cache.set_table(self.path, self._staging_buffer, get_auth())

    def _initiate_upload(self) -> None:
        pass

    def _fetch_range(self, start: int, end: int) -> bytes:
        self._staging_buffer.seek(start)
        count = end - start
        return self._staging_buffer.read(count)
