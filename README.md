# django-yandex-smartcaptcha

[Yandex SmartCaptcha](https://yandex.cloud/ru/docs/smartcaptcha/) form field for Django.
No dependencies beyond Django; the token is checked with the standard library.

*Поле формы Django с капчей Yandex SmartCaptcha. Описание по-русски — ниже.*

## Install

```bash
pip install "django-yandex-smartcaptcha @ https://github.com/Iv/django-yandex-smartcaptcha/archive/refs/tags/v0.1.1.tar.gz"
```

The tag archive needs no `git`, so it also works in slim Docker images (`git+https://…@v0.1.1` needs git).

```python
INSTALLED_APPS = [
    # ...
    "yandex_smartcaptcha",
]

SMARTCAPTCHA_CLIENT_KEY = "ysc1_..."                        # public, goes into the page
SMARTCAPTCHA_SERVER_KEY = os.environ["SMARTCAPTCHA_SERVER_KEY"]  # secret
SMARTCAPTCHA_TIMEOUT = 3                                    # seconds, optional
```

Both keys are on the captcha's page in the Yandex Cloud console.

## Use

```python
from django import forms
from yandex_smartcaptcha.fields import SmartCaptchaField


class QuestionForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    captcha = SmartCaptchaField()
```

Pass the visitor's IP to Yandex (optional, improves the check):

```python
from yandex_smartcaptcha.client import client_ip

form = QuestionForm(request.POST)
form.fields["captcha"].client_ip = client_ip(request)
if form.is_valid():
    ...
```

The widget renders an empty container (`min-height: 100px`, so the page does not jump while the
widget loads, yet a taller widget does not overlap what follows); `captcha.js` puts the "I'm not a robot" button there and
adds a hidden `smart-token` input, so the token is sent with the form, including
`$(form).serialize()` in AJAX forms. A token is single-use: after an AJAX submit call
`window.smartCaptcha.reset()`.

### Options

- `SmartCaptchaField(load_script=False)` — the widget does not load `captcha.js`; the page loads
  `https://smartcaptcha.cloud.yandex.ru/captcha.js` itself, e.g. only when a hidden form is opened.
  The script renders every `div.smart-captcha` present when it loads.
- `SmartCaptchaField(language="en")` — widget language; by default the active Django language.
- Optional captcha while keys are not configured:

  ```python
  from yandex_smartcaptcha.conf import captcha_enabled

  class QuestionForm(forms.Form):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          if captcha_enabled():
              self.fields["captcha"] = SmartCaptchaField()
  ```

### When Yandex is unreachable

As Yandex recommends, if the validation request fails (network error, timeout, 5xx) the form is
**allowed**, so an outage does not block visitors; a warning is logged. A 4xx answer usually
means a wrong server key: the form is allowed too, and the problem is logged as an error
(logger `yandex_smartcaptcha.client`).

## По-русски

Поле `SmartCaptchaField` для форм Django. Ключи — в настройках `SMARTCAPTCHA_CLIENT_KEY`
(публичный, ysc1_…) и `SMARTCAPTCHA_SERVER_KEY` (секретный, ysc2_…, лучше из окружения).
Сообщение об ошибке переведено на русский.

- `load_script=False` — скрипт капчи подключает сама страница (например, только когда посетитель
  открыл форму), а не каждая страница с формой.
- IP посетителя: `form.fields["captcha"].client_ip = client_ip(request)` — за прокси берется
  первый адрес из `X-Forwarded-For`.
- Если сервис проверки недоступен, форма проходит (так советует Яндекс), в лог пишется
  предупреждение; ответ 4xx (скорее всего неверный ключ сервера) пишется как ошибка.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

The Russian translation is compiled into `locale/ru/LC_MESSAGES/django.mo`; after editing the
`.po` file run `django-admin compilemessages` in `yandex_smartcaptcha/`.

## License

MIT
