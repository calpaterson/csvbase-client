import requests

@dataclass
class Response:
    content_type: str
    stream: IO[bytes]

    def as_content_type(content_type: str) -> IO[bytes]

class CSVBaseClient:
    """A (caching) client for csvbase."""
    def __init__(self):
        self.http_client = requests.Session()
        self.connect_timeout = 6.05
        self.read_timeout = 60

    def get(self, username, table_name) -> Table:
        ...
