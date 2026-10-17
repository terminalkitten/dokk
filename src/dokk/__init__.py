__version__ = "0.0.1"


class DokkError(Exception):
    """A user-facing build error. The CLI prints the message without a traceback."""
