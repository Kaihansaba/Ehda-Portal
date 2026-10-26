
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class SprintOneAuthenticationTests(TestCase):

    def setUp(self):
        self.donor = User.objects.create_user(
            email="donor@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="Donor",
            phone="0700000001",
            role="DONOR",
        )

        self.hospital = User.objects.create_user(
            email="hospital@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="Hospital",
            phone="0700000003",
            role="HOSPITAL",
        )

    # 1. Registration validation tests

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Another",
                "last_name": "Donor",
                "email": "donor@example.com",
                "phone": "0700000002",
                "role": "DONOR",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors.get("email"))
        self.assertEqual(
            User.objects.filter(email="donor@example.com").count(),
            1,
        )

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "Donor",
                "email": "newdonor@example.com",
                "phone": "0700000002",
                "role": "DONOR",
                "password": "StrongPass123!",
                "confirm_password": "DifferentPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.context["form"].errors.get("confirm_password")
        )
        self.assertFalse(
            User.objects.filter(email="newdonor@example.com").exists()
        )

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "New",
                "last_name": "Donor",
                "email": "weakpass@example.com",
                "phone": "0700000002",
                "role": "DONOR",
                "password": "123",
                "confirm_password": "123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors.get("password"))
        self.assertFalse(
            User.objects.filter(email="weakpass@example.com").exists()
        )

    # 2. Login tests

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "donor@example.com",
                "password": "StrongPass123!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(
            response.request["PATH_INFO"],
            reverse("donor_dashboard"),
        )

    def test_login_with_invalid_password(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "donor@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    # 3. Donor profile tests

    def test_donor_can_open_profile(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_profile"))

        self.assertEqual(response.status_code, 200)

    def test_donor_can_update_profile(self):
        self.client.force_login(self.donor)

        response = self.client.post(
            reverse("donor_profile"),
            {
                "first_name": "Updated",
                "last_name": "Donor",
                "email": "donor@example.com",
                "phone": "0700000009",
                "blood_type": "O+",
            },
        )

        self.donor.refresh_from_db()

        self.assertRedirects(response, reverse("donor_profile"))
        self.assertEqual(self.donor.first_name, "Updated")
        self.assertEqual(self.donor.phone, "0700000009")
        self.assertEqual(self.donor.blood_type, "O+")

    def test_profile_rejects_duplicate_email(self):
        self.client.force_login(self.donor)

        response = self.client.post(
            reverse("donor_profile"),
            {
                "first_name": "Test",
                "last_name": "Donor",
                "email": "hospital@example.com",
                "phone": "0700000001",
                "blood_type": "O+",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors.get("email"))

        self.donor.refresh_from_db()
        self.assertEqual(self.donor.email, "donor@example.com")

    # 4. Availability tests

    def test_donor_can_toggle_availability(self):
        self.client.force_login(self.donor)

        self.assertTrue(self.donor.is_available)

        response = self.client.post(reverse("toggle_availability"))

        self.donor.refresh_from_db()

        self.assertRedirects(response, reverse("donor_dashboard"))
        self.assertFalse(self.donor.is_available)

    def test_get_request_does_not_toggle_availability(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("toggle_availability"))

        self.donor.refresh_from_db()

        self.assertRedirects(response, reverse("donor_dashboard"))
        self.assertTrue(self.donor.is_available)

    # 5. Role permission tests

    def test_hospital_cannot_open_donor_profile(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("donor_profile"))

        self.assertEqual(response.status_code, 403)

    def test_hospital_cannot_toggle_donor_availability(self):
        self.client.force_login(self.hospital)

        response = self.client.post(reverse("toggle_availability"))

        self.assertEqual(response.status_code, 403)

        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_available)

    def test_donor_cannot_open_hospital_dashboard(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("hospital_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_donor_cannot_open_admin_dashboard(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_hospital_cannot_open_admin_dashboard(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_admin_can_open_admin_dashboard(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="Admin",
            phone="0700000004",
            role="ADMIN",
        )

        self.client.force_login(admin)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_open_donor_dashboard(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="Admin",
            phone="0700000004",
            role="ADMIN",
        )

        self.client.force_login(admin)

        response = self.client.get(reverse("donor_dashboard"))

        self.assertEqual(response.status_code, 403)

    # 6. Logout and authentication protection tests

    def test_logged_in_user_can_logout_with_post(self):
        self.client.force_login(self.donor)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))

        dashboard_response = self.client.get(reverse("donor_dashboard"))

        self.assertRedirects(
            dashboard_response,
            f"{reverse('login')}?next={reverse('donor_dashboard')}",
        )

    def test_get_request_does_not_logout_user(self):
        self.client.force_login(self.donor)

        self.client.get(reverse("logout"))

        dashboard_response = self.client.get(reverse("donor_dashboard"))

        self.assertEqual(dashboard_response.status_code, 200)

    def test_logged_out_user_cannot_access_donor_dashboard(self):
        response = self.client.get(reverse("donor_dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('donor_dashboard')}",
        )

    def test_hospital_can_create_blood_request(self):
        self.client.force_login(self.hospital)

        response = self.client.post(
            reverse("create_blood_request"),
            {
                "blood_type": "O+",
                "units_needed": 2,
                "urgency": "URGENT",
                "notes": "Need blood for emergency treatment.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.hospital.blood_requests.filter(blood_type="O+").exists()
        )

    def test_hospital_can_view_blood_requests(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("manage_blood_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("requests", response.context)

    def test_hospital_request_rejects_invalid_units(self):
        self.client.force_login(self.hospital)

        response = self.client.post(
            reverse("create_blood_request"),
            {
                "blood_type": "O+",
                "units_needed": 0,
                "urgency": "ROUTINE",
                "notes": "Need blood.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("units_needed", response.context["form"].errors)

    def test_hospital_request_requires_notes_for_urgent_requests(self):
        self.client.force_login(self.hospital)

        response = self.client.post(
            reverse("create_blood_request"),
            {
                "blood_type": "A-",
                "units_needed": 2,
                "urgency": "URGENT",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("notes", response.context["form"].errors)
