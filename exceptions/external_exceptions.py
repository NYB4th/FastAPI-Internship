class UpstreamNotFoundError(Exception):
    """Raised when external resource returns HTTP 404."""

    pass


class UpstreamTimeoutError(Exception):
    """Raised when the external request times out."""

    pass


class UpstreamApiError(Exception):
    """Raised for connection errors or 5xx upstream failures."""

    pass
