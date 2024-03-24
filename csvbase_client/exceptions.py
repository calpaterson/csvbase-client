import requests


def http_error_to_user_message(ref: str, response: requests.Response) -> str:
    """Convert http responses into user-visible error messages"""
    if response.status_code == 404:
        return f"Table not found: {ref}"
    else:
        return f"Unknown error (HTTP status code: {response.status_code})"


class CSVBaseException(Exception):
    """Catch all exception for errors.

    Eventually this will be subclassed to allow for people to determine which
    error has occurred, but not just yet.

    """
