"""CG errors."""


class RayvisionError(Exception):
    """Raise RayvisionError if something wrong."""

    def __init__(self, error_code, error, *args, **kwargs):
        """Initialize error message, inherited Exception.

        Args:
            error_code (int): Error status code.
            error (str): Error message.
            args (set): Other parameters.
            kwargs (dict): Other keyword parameters.

        """
        super(RayvisionError, self).__init__(self, error, *args, **kwargs)
        self.error_code = error_code
        self.error = error


class UnsupportedDatabaseError(Exception):
    """The local database supports only Redis and Sqlite"""


class UnsupportedEngineType(Exception):
    """Engine Only Support aspera and raysyncproxy"""


class DownloadFailed(Exception):
    """Download failed"""

    def __init__(self, error, *args, **kwargs):
        """Initialize error message, inherited Exception.

        Args:
            error (str): Error message.
            args (set): Other parameters.
            kwargs (dict): Other keyword parameters.

        """
        super(DownloadFailed, self).__init__(self, error, *args, **kwargs)
        self.error = error
