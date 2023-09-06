from unittest.mock import patch
import string
import contextlib
import random


def format_response_error(response) -> str:
    if response.headers.get("Content-Type") == "application/json":
        return response.json()
    else:
        return response.content
