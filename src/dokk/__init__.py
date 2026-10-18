from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dokk")  # set from the git tag at build time (hatch-vcs)
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0"


class DokkError(Exception):
    """A user-facing build error. The CLI prints the message without a traceback."""
