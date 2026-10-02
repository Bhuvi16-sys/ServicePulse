"""
ServicePulse - Monitoring engine.

Member 2: Monitoring & Networking
Provides the high-level service check used by the GUI, database,
analytics and automation modules.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime

from .network import DEFAULT_TIMEOUT, InvalidURLError, send_http_request


logger = logging.getLogger(__name__)


@dataclass
class MonitoringResult:
    """Standard result returned after checking one service."""

    status: str
    status_code: int | None
    response_time: float | None
    checked_at: str
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def classify_status(status_code: int) -> str:
    """
    Classify an HTTP response for ServicePulse.

    2xx and 3xx responses are considered UP.
    4xx and 5xx responses are considered DOWN.
    """
    if 200 <= status_code < 400:
        return "UP"

    return "DOWN"


def check_service(url: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """
    Check one website/API and return a consistent monitoring result.

    This function does NOT write to the database.
    Member 3 owns persistence.

    Returned fields match the data needed by:
        save_monitoring_result(
            service_id,
            status,
            status_code,
            response_time
        )
    """
    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        status_code, response_time = send_http_request(url, timeout)

        result = MonitoringResult(
            status=classify_status(status_code),
            status_code=status_code,
            response_time=response_time,
            checked_at=checked_at,
            error=None,
        )

    except InvalidURLError as error:
        result = MonitoringResult(
            status="DOWN",
            status_code=None,
            response_time=None,
            checked_at=checked_at,
            error=str(error),
        )

    except TimeoutError as error:
        result = MonitoringResult(
            status="DOWN",
            status_code=None,
            response_time=None,
            checked_at=checked_at,
            error=str(error),
        )

    except ConnectionError as error:
        result = MonitoringResult(
            status="DOWN",
            status_code=None,
            response_time=None,
            checked_at=checked_at,
            error=str(error),
        )

    except Exception as error:
        logger.exception("Unexpected monitoring error for %s", url)

        result = MonitoringResult(
            status="DOWN",
            status_code=None,
            response_time=None,
            checked_at=checked_at,
            error=f"Unexpected error: {error}",
        )

    return result.to_dict()


def check_service_object(
    url: str,
    timeout: float = DEFAULT_TIMEOUT
) -> MonitoringResult:
    """Object-oriented convenience wrapper around check_service()."""
    return MonitoringResult(**check_service(url, timeout))


if __name__ == "__main__":
    from database.db import get_services, save_monitoring_result
    
    print("Fetching services from the database...")
    services = get_services()
    
    if not services:
        print("No services found in database.")
    else:
        for svc in services:
            service_id = svc[0]
            service_name = svc[1]
            url = svc[2]
            
            print(f"Pinging {service_name} at {url}...")
            result = check_service(url)
            
            # Pass the live data to Member 3's DB function
            save_monitoring_result(
                service_id=service_id,
                status=result['status'],
                status_code=result['status_code'],
                response_time=result['response_time']
            )
            print(f"  -> Saved to database: {result['status']} ({result['response_time']} ms)")
            
        print("All live network checks successfully saved!")