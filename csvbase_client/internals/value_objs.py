import enum
from base64 import b64encode
from dataclasses import dataclass


@dataclass
class Auth:
    username: str
    api_key: str

    def as_basic_auth(self) -> str:
        user_pass = f"{self.username}:{self.api_key}".encode("utf-8")
        encoded = b64encode(user_pass).decode("utf-8")
        return f"Basic {encoded}"


@enum.unique
class ContentType(enum.Enum):
    PARQUET = 1
    CSV = 2

    def mimetype(self):
        return MIMETYPE_MAP[self]

    @staticmethod
    def from_mimetype(mimetype) -> "ContentType":
        return BACKWARD_MIMETYPE_MAP[mimetype]

    def file_extension(self) -> str:
        return FILE_EXTENSION_MAP[self]


MIMETYPE_MAP = {
    ContentType.PARQUET: "application/parquet",  # unofficial, but convenient
    ContentType.CSV: "text/csv",
}

BACKWARD_MIMETYPE_MAP = {v: k for k, v in MIMETYPE_MAP.items()}

FILE_EXTENSION_MAP = {
    ContentType.CSV: ".csv",
    ContentType.PARQUET: ".parquet",
}
