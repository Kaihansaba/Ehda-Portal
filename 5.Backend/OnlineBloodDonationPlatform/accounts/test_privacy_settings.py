"""#003: donors choose whether to share their phone and show their area."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, User
from locations.models import DonorLocation
from locations.search import search_donors


PASSWORD = "StrongPass123!"


class PrivacySettingsTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, first_name="Dina", last_name="Donoryan",
            role="DONOR", blood_type="O-", phone="0799888777",
        )
        DonorLocation.objects.create(
            user=self.donor, province="Kabul", district="Karte Seh",
            latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )

    def set(self, **settings):
        User.objects.filter(pk=self.donor.pk).update(**settings)
        self.donor.refresh_from_db()

    def test_both_settings_are_on_by_default(self):
        self.assertTrue(self.donor.share_phone_after_accept)
        self.assertTrue(self.donor.show_district)

    def test_donor_changes_settings_on_profile(self):
        self.client.force_login(self.donor)

        self.client.post(reverse("donor_profile"), {
            "first_name": "Dina", "last_name": "Donoryan", "email": "dina@example.com",
            "phone": "0799888777", "blood_type": "O-",
            # Unchecked switches are simply not sent.
        })

        self.donor.refresh_from_db()
        self.assertFalse(self.donor.share_phone_after_accept)
        self.assertFalse(self.donor.show_district)
        self.assertContains(self.client.get(reverse("donor_profile")), "Share my phone number after I accept")

    def test_search_hides_district_when_off(self):
        self.assertEqual(search_donors(self.hospital, "O-")[0].district, "Karte Seh")

        self.set(show_district=False)
        results = search_donors(self.hospital, "O-")

        self.assertEqual(len(results), 1)  # still found by blood type and province
        self.assertEqual(results[0].district, "")
        self.assertEqual(search_donors(self.hospital, "O-", district="Karte"), [])

        self.client.force_login(self.hospital)
        self.assertNotContains(self.client.get(reverse("locations:search"), {"blood_type": "O-"}), "Karte Seh")

    def test_map_leaves_out_donors_who_hide_their_area(self):
        self.client.force_login(self.hospital)
        self.assertEqual(len(self.client.get(reverse("locations:map")).context["map_data"]["donors"]), 1)

        self.set(show_district=False)

        self.assertEqual(self.client.get(reverse("locations:map")).context["map_data"]["donors"], [])

    def accept_request(self):
        blood_request = BloodRequest.objects.create(hospital=self.hospital, blood_type="A+")
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="ACCEPTED")
        return blood_request

    def test_phone_shared_after_accept_by_default(self):
        blood_request = self.accept_request()
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        self.assertContains(response, f'href="tel:{self.donor.phone}"')

    def test_phone_hidden_when_donor_turned_it_off(self):
        self.set(share_phone_after_accept=False)
        blood_request = self.accept_request()
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        self.assertNotContains(response, self.donor.phone)
        self.assertContains(response, "Phone hidden by the donor")
        # Accepting still shares the full name, and messaging stays open.
        self.assertContains(response, "Dina Donoryan")
        self.assertContains(response, reverse("conversation", args=[blood_request.pk, self.donor.pk]))

    def test_donor_is_told_their_phone_stays_private(self):
        self.set(share_phone_after_accept=False)
        blood_request = BloodRequest.objects.create(hospital=self.hospital, blood_type="A+")
        self.client.force_login(self.donor)

        response = self.client.post(
            reverse("respond_to_request", args=[blood_request.pk]), {"response": "ACCEPTED"}, follow=True,
        )

        self.assertContains(response, "Your phone number stays private.")
        self.assertNotContains(response, "can see your name and phone number")
