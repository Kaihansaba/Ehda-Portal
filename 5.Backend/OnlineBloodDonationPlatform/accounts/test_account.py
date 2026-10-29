"""#016: account details for hospitals and admins; password change for all roles."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, User


PASSWORD = "StrongPass123!"
NEW_PASSWORD = "BetterPass456!"


class AccountPageTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL", phone="0700111222",
        )
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada", last_name="Admin")
        self.url = reverse("account")

    def save(self, user, **data):
        self.client.force_login(user)
        payload = {
            "first_name": user.first_name, "last_name": user.last_name,
            "email": user.email, "phone": "0700999888", "address": "",
        }
        payload.update(data)
        return self.client.post(self.url, payload, follow=True)

    def test_hospital_updates_details_and_address(self):
        response = self.save(self.hospital, address="Darulaman Road, Kabul", phone="0700555666")

        self.hospital.refresh_from_db()
        self.assertEqual(self.hospital.address, "Darulaman Road, Kabul")
        self.assertEqual(self.hospital.phone, "0700555666")
        self.assertContains(response, "Your account details have been saved.")
        self.assertContains(response, "Hospital name")

    def test_hospital_name_can_be_one_part(self):
        self.hospital.last_name = ""
        self.hospital.save()

        response = self.save(self.hospital, last_name="", address="Kabul")

        self.assertContains(response, "Your account details have been saved.")
        self.hospital.refresh_from_db()
        self.assertEqual(self.hospital.address, "Kabul")

    def test_admin_has_no_address_field(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(self.url)

        self.assertNotIn("address", response.context["form"].fields)
        self.save(self.admin_user, first_name="Adaline", address="Should be ignored")
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, "Adaline")
        self.assertEqual(self.admin_user.address, "")

    def test_validation(self):
        response = self.save(self.hospital, email="admin@example.com")
        self.assertContains(response, "An account with this email already exists.")

        response = self.save(self.hospital, first_name="")
        self.assertTrue(response.context["form"].errors.get("first_name"))

        self.hospital.refresh_from_db()
        self.assertEqual(self.hospital.email, "hospital@example.com")
        self.assertEqual(self.hospital.first_name, "Ali Abad")

    def test_role_cannot_be_changed_here(self):
        self.save(self.hospital, role="ADMIN", is_staff="on")

        self.hospital.refresh_from_db()
        self.assertEqual(self.hospital.role, "HOSPITAL")
        self.assertFalse(self.hospital.is_staff)

    def test_donors_use_their_profile_page(self):
        donor = User.objects.create_user(email="d@example.com", password=PASSWORD, first_name="D", role="DONOR")
        self.client.force_login(donor)

        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_donor_who_accepted_sees_hospital_address(self):
        self.hospital.address = "Darulaman Road, Kabul"
        self.hospital.save()
        donor = User.objects.create_user(email="d@example.com", password=PASSWORD, first_name="D", role="DONOR", blood_type="O-")
        blood_request = BloodRequest.objects.create(hospital=self.hospital, blood_type="A+")
        self.client.force_login(donor)

        self.assertNotContains(self.client.get(reverse("donor_blood_requests")), "Darulaman Road")

        DonorResponse.objects.create(blood_request=blood_request, donor=donor, response="ACCEPTED")
        self.assertContains(self.client.get(reverse("donor_blood_requests")), "Darulaman Road")


class PasswordChangeTests(TestCase):

    def setUp(self):
        self.users = [
            User.objects.create_user(email=f"{role.lower()}@example.com", password=PASSWORD, first_name=role, role=role)
            for role in ("DONOR", "HOSPITAL")
        ] + [User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")]
        self.url = reverse("password_change")

    def test_every_role_can_change_password_and_stays_signed_in(self):
        for user in self.users:
            with self.subTest(role=user.role):
                self.client.force_login(user)
                response = self.client.post(self.url, {
                    "old_password": PASSWORD, "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD,
                }, follow=True)

                self.assertContains(response, "Password changed")
                user.refresh_from_db()
                self.assertTrue(user.check_password(NEW_PASSWORD))
                # Still signed in (session hash updated).
                self.assertEqual(self.client.get(reverse("notifications")).status_code, 200)

    def test_wrong_current_password_is_refused(self):
        self.client.force_login(self.users[0])

        response = self.client.post(self.url, {
            "old_password": "wrong", "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD,
        })

        self.assertTrue(response.context["form"].errors.get("old_password"))
        self.users[0].refresh_from_db()
        self.assertTrue(self.users[0].check_password(PASSWORD))

    def test_weak_or_mismatched_new_password_is_refused(self):
        self.client.force_login(self.users[0])

        for new1, new2 in (("123", "123"), (NEW_PASSWORD, "Different789!")):
            with self.subTest(new=new1):
                response = self.client.post(self.url, {
                    "old_password": PASSWORD, "new_password1": new1, "new_password2": new2,
                })
                self.assertTrue(response.context["form"].errors)

    def test_page_uses_site_design_and_needs_login(self):
        self.client.force_login(self.users[0])
        self.assertContains(self.client.get(self.url), "css/ehda.css")

        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")
