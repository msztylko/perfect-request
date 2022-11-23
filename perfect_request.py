import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, ReadTimeout
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = (3.05, 10)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def perfect_session() -> requests.Session:
    retry = Retry(
        total=3,
        read=10,
        connect=3.05,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )

    session = requests.Session()
    adapter = TimeoutHTTPAdapter(timeout=(3.05, 10), max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def get_request(url: str, session: requests.Session) -> Optional[requests.Response]:
    try:
        response = session.get(url)
    except ConnectionError:
        logger.exception(f"Could not connect to {url}")
        return None
    except ReadTimeout:
        logger.exception(f"Read timed out on connection to {url}")
        return None
    except Exception:
        logger.exception(f"General error while connecting to {url}")
        return None
    else:
        if response:
            logger.info(f"Got correct response from {url}")
        else:
            logger.warning(f"Got incorrect response from {url}")
        return response
