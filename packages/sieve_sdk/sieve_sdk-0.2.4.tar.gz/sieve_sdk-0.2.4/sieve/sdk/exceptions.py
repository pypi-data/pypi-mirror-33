class UnexpectedStatusCode(Exception):
    """
    Raised when an api returns an unprocessable or unexpected status code
    """


class UnexpectedResourceResponse(Exception):
    """
    Raised when an api returns an unprocessable or unexpected response content
    """