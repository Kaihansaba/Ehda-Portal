from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, User


PASSWORD = "StrongPass123!"

ADMIN_PAGES = (
    "admin_manage_users",
    "admin_manage_hospitals",
    "admin_reported_accounts",
    "admin_platform_activity",
    "admin_platform_statistics",
    "admin_security_access",
)


class AdminToolsTests(TestCase):
    """Admin pages from Shafiqa's Sprint 4 branch."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password=PASSWORD,
            first_name="Test", last_name="Admin", phone="0700000004",
        )
        self.donor = User.objects.create_user(
            email="donor@example.com", password=PASSWORD,
            first_name="Test", last_name="Donor", role="DONOR",
        )
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD,
            first_name="City", last_name="Hospital", phone="0700000003", role="HOSPITAL",
        )
        self.client.force_login(self.admin_user)

    def test_admin_can_view_user_management_page(self):
        response = self.client.get(reverse("admin_manage_users"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.context)
        self.assertContains(response, self.donor.email)
        self.assertContains(response, self.hospital.email)

    def test_admin_can_view_hospital_management_page(self):
        response = self.client.get(reverse("admin_manage_hospitals"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("hospitals", response.context)
        self.assertContains(response, self.hospital.email)
        self.assertNotContains(response, self.donor.email)

    def test_admin_can_view_reported_accounts(self):
        reported_user = User.objects.create_user(
            email="reported@example.com", password=PASSWORD,
            first_name="Reported", last_name="User", role="DONOR", is_active=False,
        )

        response = self.client.get(reverse("admin_reported_accounts"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["reported_users"]), [reported_user])
        self.assertContains(response, reported_user.email)
        self.assertNotContains(response, self.donor.email)

    def test_admin_can_view_platform_activity_page(self):
        BloodRequest.objects.create(hospital=self.hospital, blood_type="O+", notes="Surgery")
        BloodRequest.objects.create(
            hospital=self.hospital, blood_type="A-", status=BloodRequest.Status.COMPLETED,
        )

        response = self.client.get(reverse("admin_platform_activity"))

        self.assertEqual(response.status_code, 200)
        summary = response.context["summary"]
        self.assertEqual(summary["total_requests"], 2)
        self.assertEqual(summary["open_requests"], 1)
        self.assertEqual(summary["completed_requests"], 1)
        self.assertEqual(len(response.context["recent_requests"]), 2)
        # The loop variable must not hide Django's request: the navbar still
        # shows the signed-in admin's name.
        self.assertContains(response, self.admin_user.first_name)

    def test_platform_statistics(self):
        User.objects.filter(pk=self.donor.pk).update(is_active=False)

        response = self.client.get(reverse("admin_platform_statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_users"], 3)
        self.assertEqual(response.context["active_users"], 2)
        self.assertEqual(response.context["inactive_users"], 1)

    def test_security_access_summary(self):
        response = self.client.get(reverse("admin_security_access"))

        self.assertEqual(response.status_code, 200)
        summary = response.context["summary"]
        self.assertEqual(summary["admins"], 1)
        self.assertEqual(summary["donors"], 1)
        self.assertEqual(summary["hospitals"], 1)

    def test_admin_can_toggle_user_status(self):
        response = self.client.post(reverse("toggle_user_status", args=[self.donor.pk]))

        self.assertRedirects(response, reverse("admin_manage_users"))
        self.donor.refresh_from_db()
        self.assertFalse(self.donor.is_active)

        self.client.post(reverse("toggle_user_status", args=[self.donor.pk]))
        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_active)

    def test_deactivated_user_cannot_log_in(self):
        self.client.post(reverse("toggle_user_status", args=[self.donor.pk]))
        self.client.logout()

        response = self.client.post(
            reverse("login"), {"email": self.donor.email, "password": PASSWORD},
        )

        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.status_code, 200)

    def test_toggle_returns_to_the_page_it_came_from(self):
        response = self.client.post(
            reverse("toggle_user_status", args=[self.hospital.pk]),
            {"next": "admin_manage_hospitals"},
        )

        self.assertRedirects(response, reverse("admin_manage_hospitals"))

    def test_toggle_ignores_unknown_next(self):
        for next_value in ("https://evil.example.com/", "//evil.example.com", "logout"):
            with self.subTest(next=next_value):
                response = self.client.post(
                    reverse("toggle_user_status", args=[self.donor.pk]),
                    {"next": next_value},
                )
                self.assertRedirects(response, reverse("admin_manage_users"))

    def test_get_does_not_toggle(self):
        response = self.client.get(reverse("toggle_user_status", args=[self.donor.pk]))

        self.assertRedirects(response, reverse("admin_manage_users"))
        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_active)

    def test_admin_cannot_deactivate_themselves(self):
        response = self.client.post(
            reverse("toggle_user_status", args=[self.admin_user.pk]), follow=True,
        )

        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
        self.assertContains(response, "deactivate your own account")

    def test_toggle_unknown_user_is_404(self):
        response = self.client.post(reverse("toggle_user_status", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_other_roles_cannot_use_admin_tools(self):
        for user in (self.donor, self.hospital):
            self.client.force_login(user)
            for name in ADMIN_PAGES:
                with self.subTest(role=user.role, page=name):
                    self.assertEqual(self.client.get(reverse(name)).status_code, 403)

            with self.subTest(role=user.role, page="toggle_user_status"):
                response = self.client.post(reverse("toggle_user_status", args=[self.admin_user.pk]))
                self.assertEqual(response.status_code, 403)

        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)


class RegistrationStaysSafeTests(TestCase):
    """Shafiqa's sign-up changes were not ported; these guard against them."""

    def test_admin_is_not_a_sign_up_choice(self):
        response = self.client.post(reverse("register"), {
            "first_name": "Eve", "last_name": "Admin", "email": "eve@example.com",
            "phone": "0700000009", "role": "ADMIN",
            "password": PASSWORD, "confirm_password": PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="eve@example.com").exists())

    def test_deactivated_email_cannot_be_re_registered(self):
        donor = User.objects.create_user(
            email="donor@example.com", password=PASSWORD, first_name="Test", role="DONOR",
            is_active=False,
        )

        self.client.post(reverse("register"), {
            "first_name": "Someone", "last_name": "Else", "email": "donor@example.com",
            "phone": "0700000002", "role": "DONOR",
            "password": "NewStrongPass123!", "confirm_password": "NewStrongPass123!",
        })

        donor.refresh_from_db()
        self.assertFalse(donor.is_active)
        self.assertTrue(donor.check_password(PASSWORD))
