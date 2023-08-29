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
