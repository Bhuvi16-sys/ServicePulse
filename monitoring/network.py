"""
ServicePulse - Network utilities.

Member 2: Monitoring & Networking
Handles URL validation and low-level HTTP requests.
"""

from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse


DEFAULT_TIMEOUT = 10
USER_AGENT = "ServicePulse/1.0"


class NetworkError(Exception):
    """Base exception for ServicePulse networking errors."""


class InvalidURLError(NetworkError):
    """Raised when a URL is missing or does not use HTTP/HTTPS."""


def validate_url(url: str) -> str:
    """Validate and normalize an HTTP/HTTPS URL."""
    if not isinstance(url, str):
        raise InvalidURLError("URL must be a string.")

    url = url.strip()

    if not url:
        raise InvalidURLError("URL cannot be empty.")

    parsed = urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise InvalidURLError("URL must start with http:// or https://.")

    if not parsed.netloc:
        raise InvalidURLError("URL must contain a valid host.")

    if any(char.isspace() for char in url):
        raise InvalidURLError("URL cannot contain whitespace.")

    return url


def send_http_request(url: str, timeout: float = DEFAULT_TIMEOUT):
    """
    Send an HTTP GET request and measure elapsed time.

    Returns:
        (status_code, response_time_ms)

    HTTP errors such as 404/500 are returned as status codes because
    the server successfully responded. The monitoring layer classifies them.
    """
    normalized_url = validate_url(url)

    if timeout <= 0:
        raise ValueError("Timeout must be greater than 0.")

    request = Request(
        normalized_url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )

    start = perf_counter()

    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = response.getcode()
            response.read(1)
    except HTTPError as error:
        status_code = error.code
    except TimeoutError as error:
        raise TimeoutError(
            f"Request timed out after {timeout:g} seconds."
        ) from error
    except URLError as error:
        reason = getattr(error, "reason", error)

        if isinstance(reason, TimeoutError):
            raise TimeoutError(
                f"Request timed out after {timeout:g} seconds."
            ) from error

        raise ConnectionError(f"Connection failed: {reason}") from error
    except OSError as error:
        raise ConnectionError(f"Connection failed: {error}") from error

    response_time_ms = round((perf_counter() - start) * 1000, 2)

    return status_code, response_time_ms
