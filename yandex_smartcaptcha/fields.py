from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from . import conf
from .client import check_token


class SmartCaptchaWidget(forms.Widget):
    """Container where captcha.js puts the "I'm not a robot" button.

    The token comes back in the ``smart-token`` field that captcha.js adds inside the container.
    With ``load_script=False`` the page loads captcha.js itself (e.g. only when a form is opened).
    """

    template_name = "yandex_smartcaptcha/widget.html"

    def __init__(self, attrs=None, load_script=True, language=None):
        super().__init__(attrs)
        self.load_script = load_script
        self.language = language

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update(
            client_key=conf.client_key(),
            language=self.language or (get_language() or "ru")[:2],
            load_script=self.load_script,
            script_url=conf.SCRIPT_URL,
        )
        return context

    def value_from_datadict(self, data, files, name):
        return data.get("smart-token")

    def value_omitted_from_data(self, data, files, name):
        return "smart-token" not in data


class SmartCaptchaField(forms.Field):
    """Form field that validates the SmartCaptcha token.

    Set ``field.client_ip`` (see ``client.client_ip``) before validation to pass the visitor's IP.
    """

    widget = SmartCaptchaWidget
    default_error_messages = {"invalid": _("Confirm that you are not a robot.")}

    def __init__(self, *, load_script=True, language=None, **kwargs):
        kwargs.setdefault("label", "")
        kwargs.setdefault("widget", SmartCaptchaWidget(load_script=load_script, language=language))
        super().__init__(**kwargs)
        self.client_ip = ""
        self.error_messages["required"] = self.error_messages["invalid"]

    def validate(self, value):
        super().validate(value)
        if not check_token(value, self.client_ip):
            raise ValidationError(self.error_messages["invalid"], code="invalid")
