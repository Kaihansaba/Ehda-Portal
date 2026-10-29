import datetime

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from accounts.admin import DonationAdmin
from accounts.models import Donation, User


PASSWORD = "StrongPass123!"


class AdminDashboardStatsTests(TestCase):
    """Platform numbers on the admin dashboard (Samira's and Shafiqa's work)."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password=PASSWORD, first_name="Ada",
        )
        for i in range(3):
            User.objects.create_user(
                email=f"donor{i}@example.com", password=PASSWORD,
                first_name="Don", role="DONOR",
            )
        User.objects.create_user(
            email="hospital@example.com", password=PASSWORD,
            first_name="City", role="HOSPITAL",
        )
        self.client.force_login(self.admin_user)

    def test_counts_users_by_role(self):
        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_users"], 5)
        self.assertEqual(response.context["donor_count"], 3)
        self.assertEqual(response.context["hospital_count"], 1)
        self.assertEqual(response.context["open_report_count"], 0)

    def test_numbers_are_shown_instead_of_coming_soon(self):
        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, '<div class="stat-value">5</div>', html=True)
        self.assertContains(response, '<div class="stat-value">3</div>', html=True)
        self.assertContains(response, '<div class="stat-value">1</div>', html=True)
        self.assertNotContains(response, "Coming soon")

    def test_deactivated_accounts_are_not_counted_as_reports(self):
        User.objects.filter(email="donor0@example.com").update(is_active=False)

        response = self.client.get(reverse("admin_dashboard"))

        # Still a donor; reports are separate (#019).
        self.assertEqual(response.context["donor_count"], 3)
        self.assertEqual(response.context["open_report_count"], 0)

    def test_links_to_every_admin_tool(self):
        response = self.client.get(reverse("admin_dashboard"))

        for name in (
            "admin_manage_users", "admin_manage_hospitals", "admin_reported_accounts",
            "admin_platform_activity", "admin_platform_statistics", "admin_security_access",
        ):
            with self.subTest(page=name):
                self.assertContains(response, reverse(name))

    def test_links_to_donation_records(self):
        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, reverse("admin:accounts_donation_changelist"))


class DonationAdminTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password=PASSWORD, first_name="Ada",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD,
            first_name="Dina", last_name="Donor", role="DONOR", blood_type="O-",
        )
        Donation.objects.create(
            donor=self.donor, donation_date=datetime.date(2026, 5, 1), blood_type="O-",
        )
        self.client.force_login(self.admin_user)

    def test_donation_is_registered(self):
        self.assertIsInstance(admin.site._registry[Donation], DonationAdmin)

    def test_search_by_donor_name(self):
        url = reverse("admin:accounts_donation_changelist")

        found = self.client.get(url, {"q": "Dina"})
        missing = self.client.get(url, {"q": "Nobody"})

        self.assertEqual(found.context["cl"].result_count, 1)
        self.assertEqual(missing.context["cl"].result_count, 0)

    def test_filter_by_blood_type(self):
        url = reverse("admin:accounts_donation_changelist")

        response = self.client.get(url, {"blood_type": "A+"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cl"].result_count, 0)
