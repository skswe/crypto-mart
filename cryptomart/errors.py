class MissingDataError(Exception):
    """Data is unexpectedly missing from an API call"""

    pass


class NotSupportedError(Exception):
    """Exchange does not support a built-in Enum"""

    pass

class APIError(Exception):
    """Invalid or unexpected response from an external API"""

    pass