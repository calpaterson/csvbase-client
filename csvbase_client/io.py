# FIXME: copy tests for this
from typing import Protocol


class Seekable(Protocol):
    """A file that support seeking (don't care whether text or binary)."""

    def seek(self, offset: int, whence: int = 0) -> int:
        pass


class rewind:
    """Ensure that a stream is rewound after doing something.

    This is a common error and usually subtly messes up a sequence of
    operations on a file.
    """

    def __init__(self, stream: Seekable) -> None:
        self.stream = stream

    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stream.seek(0)
