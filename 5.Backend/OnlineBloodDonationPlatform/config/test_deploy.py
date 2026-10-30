"""Deployment settings (PythonAnywhere: DEBUG off, HTTPS proxy, SQLite)."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from locations.models import Facility


PRODUCTION_ENV = {
    "DJANGO_DEBUG": "False",
    "DJANGO_SECRET_KEY": "k9#Fq2-real-looking-secret-key-for-tests-only-x7Lp0z!vB4n",
    "DJANGO_ALLOWED_HOSTS": "ehdaportal.pythonanywhere.com",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://ehdaportal.pythonanywhere.com",
}

SHOW_SETTINGS = """
import json, django
django.setup()
from django.conf import settings as s
print(json.dumps({
    "DEBUG": s.DEBUG,
    "ALLOWED_HOSTS": s.ALLOWED_HOSTS,
    "CSRF_TRUSTED_ORIGINS": s.CSRF_TRUSTED_ORIGINS,
    "STATIC_ROOT": str(s.STATIC_ROOT),
    "SECURE_PROXY_SSL_HEADER": s.SECURE_PROXY_SSL_HEADER,
    "SESSION_COOKIE_SECURE": s.SESSION_COOKIE_SECURE,
    "CSRF_COOKIE_SECURE": s.CSRF_COOKIE_SECURE,
    "SECURE_SSL_REDIRECT": s.SECURE_SSL_REDIRECT,
    "EMAIL_BACKEND": s.EMAIL_BACKEND,
    "SECURE_REFERRER_POLICY": s.SECURE_REFERRER_POLICY,
}))
"""


def run_python(code, **env):
    """Run code with the project's settings in a fresh process."""
    environment = {
        k: v for k, v in os.environ.items()
        if not k.startswith(("DJANGO_", "EMAIL_"))
    }
    environment.update(env, DJANGO_SETTINGS_MODULE="config.settings")
    return subprocess.run(
        [sys.executable, "-c", code], cwd=settings.BASE_DIR,
        env=environment, capture_output=True, text=True,
    )


def load_settings(**env):
    result = run_python(SHOW_SETTINGS, **env)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class ProductionSettingsTests(TestCase):

    def test_production_values_from_environment(self):
        s = load_settings(**PRODUCTION_ENV)

        self.assertFalse(s["DEBUG"])
        self.assertEqual(s["ALLOWED_HOSTS"], ["ehdaportal.pythonanywhere.com"])
        self.assertEqual(s["CSRF_TRUSTED_ORIGINS"], ["https://ehdaportal.pythonanywhere.com"])
        self.assertEqual(s["SECURE_PROXY_SSL_HEADER"], ["HTTP_X_FORWARDED_PROTO", "https"])
        self.assertTrue(s["SESSION_COOKIE_SECURE"])
        self.assertTrue(s["CSRF_COOKIE_SECURE"])
        self.assertFalse(s["SECURE_SSL_REDIRECT"])
        self.assertEqual(s["SECURE_REFERRER_POLICY"], "strict-origin-when-cross-origin")
        self.assertTrue(s["STATIC_ROOT"].endswith("staticfiles"))

    def test_local_defaults(self):
        s = load_settings()

        self.assertTrue(s["DEBUG"])
        self.assertFalse(s["SESSION_COOKIE_SECURE"])
        self.assertIsNone(s["SECURE_PROXY_SSL_HEADER"])
        self.assertEqual(s["CSRF_TRUSTED_ORIGINS"], [])

    def test_lists_ignore_spaces_and_empty_items(self):
        s = load_settings(**{**PRODUCTION_ENV, "DJANGO_ALLOWED_HOSTS": " a.example.org , ,b.example.org "})

        self.assertEqual(s["ALLOWED_HOSTS"], ["a.example.org", "b.example.org"])

    def test_email_is_console_unless_smtp_login_is_set(self):
        self.assertEqual(load_settings()["EMAIL_BACKEND"], "django.core.mail.backends.console.EmailBackend")
        self.assertEqual(
            load_settings(EMAIL_HOST_USER="ehda@example.com")["EMAIL_BACKEND"],
            "django.core.mail.backends.console.EmailBackend",
        )
        self.assertEqual(
            load_settings(EMAIL_HOST_USER="ehda@example.com", EMAIL_HOST_PASSWORD="app-password")["EMAIL_BACKEND"],
            "config.email.SafeSMTPEmailBackend",
        )

    def test_check_deploy_passes(self):
        result = run_python(
            "import django, sys; django.setup();"
            "from django.core.management import call_command;"
            "call_command('check', deploy=True, fail_level='WARNING')",
            **PRODUCTION_ENV, DJANGO_SECURE_HSTS_SECONDS="3600",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_deploy_only_mentions_hsts_when_it_is_off(self):
        result = run_python(
            "import django; django.setup();"
            "from django.core.management import call_command;"
            "call_command('check', deploy=True)",
            **PRODUCTION_ENV,
        )

        warnings = sorted(set(w for w in ("W004", "W008", "W012", "W016", "W018", "W020", "W009") if w in result.stderr + result.stdout))
        self.assertEqual(warnings, ["W004"], result.stdout + result.stderr)


class SafeEmailTests(TestCase):

    @override_settings(
        EMAIL_BACKEND="config.email.SafeSMTPEmailBackend",
        EMAIL_HOST="127.0.0.1", EMAIL_PORT=1, EMAIL_TIMEOUT=2, EMAIL_USE_TLS=False,
    )
    def test_password_reset_still_works_when_smtp_is_unreachable(self):
        User.objects.create_user(email="dina@example.com", password="StrongPass123!", first_name="Dina")

        with self.assertLogs("config.email", level="ERROR"):
            response = self.client.post(reverse("password_reset"), {"email": "dina@example.com"})

        self.assertRedirects(response, reverse("password_reset_done"))


class StaticAndDataTests(TestCase):

    def test_collectstatic_gathers_site_and_admin_files(self):
        with tempfile.TemporaryDirectory() as root, override_settings(STATIC_ROOT=root):
            call_command("collectstatic", interactive=False, verbosity=0)

            for path in ("css/ehda.css", "css/ehda-admin.css", "js/ehda.js", "js/maps.js",
                         "img/favicon.svg", "admin/css/base.css"):
                with self.subTest(path=path):
                    self.assertTrue((Path(root) / path).exists())

    def test_sample_facilities_exist_after_migrate(self):
        # The test database is built by running every migration on an
        # empty database, like a first deploy.
        self.assertGreater(Facility.objects.filter(is_active=True).count(), 0)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_error_pages_with_debug_off(self):
        response = self.client.get("/no-such-page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertNotContains(response, "Traceback", status_code=404)
