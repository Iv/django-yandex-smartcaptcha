import io
import json
from unittest import mock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

from django import forms
from django.test import RequestFactory, override_settings

from yandex_smartcaptcha.client import check_token, client_ip
from yandex_smartcaptcha.conf import captcha_enabled
from yandex_smartcaptcha.fields import SmartCaptchaField


class QuestionForm(forms.Form):
    text = forms.CharField()
    captcha = SmartCaptchaField()


def yandex_answers(status):
    def fake_urlopen(request, timeout):
        fake_urlopen.sent = parse_qs(request.data.decode())
        return io.BytesIO(json.dumps({"status": status}).encode())

    return fake_urlopen


def test_valid_token_passes_with_ip():
    fake = yandex_answers("ok")
    form = QuestionForm({"text": "hi", "smart-token": "tok"})
    form.fields["captcha"].client_ip = "1.2.3.4"
    with mock.patch("yandex_smartcaptcha.client.urlopen", fake):
        assert form.is_valid()
    assert fake.sent == {"secret": ["ysc2_server"], "token": ["tok"], "ip": ["1.2.3.4"]}


def test_rejected_token_fails():
    form = QuestionForm({"text": "hi", "smart-token": "tok"})
    with mock.patch("yandex_smartcaptcha.client.urlopen", yandex_answers("failed")):
        assert not form.is_valid()
    assert form.errors["captcha"] == ["Подтвердите, что вы не робот."]


def test_missing_token_fails_without_request():
    form = QuestionForm({"text": "hi"})
    with mock.patch("yandex_smartcaptcha.client.urlopen") as urlopen:
        assert not form.is_valid()
    assert "captcha" in form.errors
    urlopen.assert_not_called()


def test_service_outage_allows():
    with mock.patch("yandex_smartcaptcha.client.urlopen", side_effect=URLError("down")):
        assert check_token("tok")
    with mock.patch("yandex_smartcaptcha.client.urlopen", side_effect=TimeoutError()):
        assert check_token("tok")


def test_wrong_key_allows_and_logs_error(caplog):
    error = HTTPError("https://x", 403, "Forbidden", {}, None)
    with mock.patch("yandex_smartcaptcha.client.urlopen", side_effect=error):
        assert check_token("tok")
    assert caplog.records[-1].levelname == "ERROR"


def test_client_ip_prefers_forwarded_for():
    rf = RequestFactory()
    assert client_ip(rf.get("/", HTTP_X_FORWARDED_FOR="5.6.7.8, 10.0.0.1", REMOTE_ADDR="10.0.0.2")) == "5.6.7.8"
    assert client_ip(rf.get("/", REMOTE_ADDR="10.0.0.2")) == "10.0.0.2"


def test_widget_renders_container_and_loader():
    html = str(QuestionForm()["captcha"])
    assert 'class="smart-captcha"' in html
    assert 'data-sitekey="ysc1_client"' in html
    assert 'data-hl="ru"' in html
    assert "captcha.js" in html


def test_widget_without_script():
    class LazyForm(forms.Form):
        captcha = SmartCaptchaField(load_script=False, language="en")

    html = str(LazyForm()["captcha"])
    assert "captcha.js" not in html
    assert 'data-hl="en"' in html


def test_captcha_enabled_needs_both_keys():
    assert captcha_enabled()
    with override_settings(SMARTCAPTCHA_SERVER_KEY=""):
        assert not captcha_enabled()
