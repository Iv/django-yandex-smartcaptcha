import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import conf

logger = logging.getLogger(__name__)


def client_ip(request) -> str:
    """Visitor's IP: the first X-Forwarded-For address behind a proxy, else REMOTE_ADDR.

    The address is only a hint for Yandex's scoring, so a spoofed header does no harm.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


def check_token(token: str, ip: str = "") -> bool:
    """Whether the token passed the check.

    If the validation service fails, the request is allowed, as Yandex recommends:
    otherwise an outage on their side would block every form. A 4xx answer most
    likely means a wrong server key, so it is logged as an error.
    """
    if not token:
        return False
    data = urlencode({"secret": conf.server_key(), "token": token, "ip": ip}).encode()
    try:
        with urlopen(Request(conf.VALIDATE_URL, data=data), timeout=conf.timeout()) as resp:
            return json.loads(resp.read().decode()).get("status") == "ok"
    except HTTPError as e:
        log = logger.error if 400 <= e.code < 500 else logger.warning
        log("SmartCaptcha validation failed, allowing the request: %r", e)
        return True
    except (URLError, TimeoutError, ValueError) as e:
        logger.warning("SmartCaptcha validation failed, allowing the request: %r", e)
        return True
