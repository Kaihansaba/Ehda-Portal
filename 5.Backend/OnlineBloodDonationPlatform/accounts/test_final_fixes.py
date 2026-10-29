"""Regression tests for the fixes made in the final audit."""
import os
import subprocess
import sys

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import server_error

from accounts.models import BloodRequest, User


PASSWORD = "StrongPass123!"


class ErrorPageTests(TestCase):

    @override_settings(DEBUG=False)
    def test_404_page_uses_the_site_design(self):
        response = self.client.get("/no-such-page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, "css/ehda.css", status_code=404)

    def test_500_page_renders_without_a_request(self):
        response = server_error(RequestFactory().get("/"))

        self.assertEqual(response.status_code, 500)
        content = response.content.decode()
        self.assertIn("Something went wrong", content)
        self.assertIn("css/ehda.css", content)
        # No technical details are exposed (NFR-016).
        self.assertNotIn("Traceback", content)


class SuccessMessageTests(TestCase):

    def test_registration_shows_success_message(self):
        response = self.client.post(reverse("register"), {
            "first_name": "Nadia", "last_name": "Karimi", "email": "nadia@example.com",
            "phone": "0700123456", "role": "DONOR",
            "password": PASSWORD, "confirm_password": PASSWORD,
        }, follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assertContains(response, "Your account has been created. Please sign in.")

    def test_blood_request_creation_shows_confirmation(self):
        hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="City", role="HOSPITAL",
        )
        self.client.force_login(hospital)

        response = self.client.post(reverse("create_blood_request"), {
            "blood_type": "A+", "units_needed": 2, "urgency": "ROUTINE", "notes": "",
        }, follow=True)

        self.assertRedirects(response, reverse("manage_blood_requests"))
        self.assertEqual(BloodRequest.objects.count(), 1)
        self.assertContains(response, "Your blood request has been created.")

    def test_toggle_user_status_shows_feedback(self):
        admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")
        donor = User.objects.create_user(email="donor@example.com", password=PASSWORD, first_name="Don", role="DONOR")
        self.client.force_login(admin_user)

        response = self.client.post(reverse("toggle_user_status", args=[donor.pk]), follow=True)
        self.assertContains(response, "donor@example.com has been deactivated.")

        response = self.client.post(reverse("toggle_user_status", args=[donor.pk]), follow=True)
        self.assertContains(response, "donor@example.com has been activated.")


class SecretKeyTests(TestCase):

    def load_settings(self, **env):
        """Import the settings in a fresh Python process with the given env."""
        environment = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
        environment.update(env, DJANGO_SETTINGS_MODULE="config.settings")
        return subprocess.run(
            [sys.executable, "-c", "import django; django.setup()"],
            cwd=settings.BASE_DIR, env=environment, capture_output=True, text=True,
        )

    def test_placeholder_keys_are_rejected_when_debug_is_off(self):
        for key in ("change-me", "django-insecure-dev-only-change-this-in-production", ""):
            with self.subTest(key=key):
                result = self.load_settings(DJANGO_DEBUG="False", DJANGO_SECRET_KEY=key)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)

    def test_real_key_is_accepted_when_debug_is_off(self):
        result = self.load_settings(
            DJANGO_DEBUG="False", DJANGO_SECRET_KEY="x7#kq" * 12, DJANGO_ALLOWED_HOSTS="ehda.example.org",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
