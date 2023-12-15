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


class LaunchRaysyncfailed(Exception):
    """start Raysync client failed"""


class NotSupportfiletype(Exception):
    """file_type onlu support normal and json"""


class NotSupportTasktype(Exception):
    """file_type onlu support upload and download and upload-list"""


class NotfoundRaysyncInI(Exception):
    """not found Raysync config file cluster.xml"""


class TaskidNotexsit(Exception):
    """task_id must is exsit!"""


class TransferTimeout(Exception):
    """Transmission timeout"""


class CreatTaskFailed(Exception):
    """Create transfer task failed"""


class DownloadRaysyncFailed(Exception):
    """Download raysync failed"""


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


class RaysyncAPIError(RayvisionError):
    """Raise RaysyncAPIError."""

    def __init__(self, error_code, error, request):
        """Initialize API error message, inherited RayvisionError.

        Args:
            error_code (int): Error status code.
            error (object): Error message.
            request (str): Request url.

        """
        super(RaysyncAPIError, self).__init__(error_code, error)
        self.error_code = error_code
        self.error = error
        self.request = request

    def __str__(self):
        """Let its  object print out an error message."""
        return 'Error code: {}, Error message: {}, URL: {}'.format(
            self.error_code,
            self.error,
            self.request)
