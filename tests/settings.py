SECRET_KEY = "tests"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "yandex_smartcaptcha"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}]
USE_I18N = True
LANGUAGE_CODE = "ru"
SMARTCAPTCHA_CLIENT_KEY = "ysc1_client"
SMARTCAPTCHA_SERVER_KEY = "ysc2_server"
