from django.conf import settings

SCRIPT_URL = "https://smartcaptcha.cloud.yandex.ru/captcha.js"
VALIDATE_URL = "https://smartcaptcha.cloud.yandex.ru/validate"


def client_key() -> str:
    return getattr(settings, "SMARTCAPTCHA_CLIENT_KEY", "") or ""


def server_key() -> str:
    return getattr(settings, "SMARTCAPTCHA_SERVER_KEY", "") or ""


def timeout() -> float:
    return getattr(settings, "SMARTCAPTCHA_TIMEOUT", 3)


def captcha_enabled() -> bool:
    """Both keys are set. Without them a form can skip the captcha field (see README)."""
    return bool(client_key() and server_key())
