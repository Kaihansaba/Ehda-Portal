"""#010: a hospital sends a blood request to one donor chosen in search."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.donor_requests import requests_for_donor, unanswered_count
from accounts.models import BloodRequest, User
from locations.models import DonorLocation


PASSWORD = "StrongPass123!"


def make_donor(email, blood_type, first_name="Don", last_name="Or", location=True, **extra):
    donor = User.objects.create_user(
        email=email, password=PASSWORD, role="DONOR", blood_type=blood_type,
        first_name=first_name, last_name=last_name, phone="0799888777", **extra,
    )
    if location:
        DonorLocation.objects.create(
            user=donor, province="Kabul", latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )
    return donor


class TargetedRequestTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL",
        )
        self.dina = make_donor("dina@example.com", "O-", first_name="Dina", last_name="Donoryan")
        self.other = make_donor("other@example.com", "O-", first_name="Omar", last_name="Other")
        self.client.force_login(self.hospital)
        self.url = reverse("create_blood_request")

    def post(self, donor, **data):
        payload = {"blood_type": "A+", "units_needed": 1, "urgency": "ROUTINE", "notes": ""}
        payload.update(data)
        if donor is not None:
            payload["target_donor"] = donor.pk
        return self.client.post(self.url, payload, follow=True)

    def test_form_is_prefilled_with_the_donors_blood_type(self):
        response = self.client.get(self.url, {"donor": self.dina.pk})

        self.assertEqual(response.context["target_donor"], self.dina)
        self.assertEqual(response.context["form"].initial["blood_type"], "O-")
        self.assertContains(response, "Dina D.")
        self.assertContains(response, f'name="target_donor" value="{self.dina.pk}"')
        self.assertNotContains(response, "Donoryan")
        self.assertNotContains(response, self.dina.email)

    def test_targeted_request_is_saved_and_confirmed(self):
        response = self.post(self.dina)

        blood_request = BloodRequest.objects.get()
        self.assertEqual(blood_request.target_donor, self.dina)
        self.assertContains(response, "sent to Dina D.")
        self.assertNotContains(response, "Dina D..")

    def test_only_the_target_donor_sees_it(self):
        self.post(self.dina)
        blood_request = BloodRequest.objects.get()

        self.assertIn(blood_request, requests_for_donor(self.dina))
        self.assertNotIn(blood_request, requests_for_donor(self.other))
        self.assertEqual(unanswered_count(self.dina), 1)
        self.assertEqual(unanswered_count(self.other), 0)

        self.client.force_login(self.dina)
        self.assertContains(self.client.get(reverse("donor_blood_requests")), "Sent to you")

    def test_other_donor_cannot_answer_a_targeted_request(self):
        self.post(self.dina)
        blood_request = BloodRequest.objects.get()
        self.client.force_login(self.other)

        self.client.post(reverse("respond_to_request", args=[blood_request.pk]), {"response": "ACCEPTED"})

        self.assertFalse(blood_request.responses.exists())

    def test_normal_requests_still_go_to_all_compatible_donors(self):
        self.post(None)
        blood_request = BloodRequest.objects.get()

        self.assertIsNone(blood_request.target_donor)
        self.assertIn(blood_request, requests_for_donor(self.dina))
        self.assertIn(blood_request, requests_for_donor(self.other))

    def test_incompatible_blood_type_is_refused(self):
        ab_donor = make_donor("ab@example.com", "AB+")

        response = self.post(ab_donor, blood_type="O-")

        self.assertFalse(BloodRequest.objects.exists())
        self.assertContains(response, "can&#x27;t be given to a patient who needs O-")

    def test_unavailable_or_unknown_donor_is_not_targeted(self):
        busy = make_donor("busy@example.com", "O-", is_available=False)
        no_location = make_donor("noloc@example.com", "O-", location=False)

        for donor_id in (busy.pk, no_location.pk, 99999, "abc"):
            with self.subTest(donor=donor_id):
                response = self.client.get(self.url, {"donor": donor_id})
                self.assertIsNone(response.context["target_donor"])
                self.assertContains(response, "no longer available")

    def test_hospital_pages_show_who_it_was_sent_to(self):
        self.post(self.dina)
        blood_request = BloodRequest.objects.get()

        listing = self.client.get(reverse("manage_blood_requests"))
        detail = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        for response in (listing, detail):
            self.assertContains(response, "Dina D.")
            self.assertNotContains(response, "Donoryan")
            self.assertNotContains(response, self.dina.phone)

    def test_untargeted_detail_says_all_donors(self):
        self.post(None)
        blood_request = BloodRequest.objects.get()

        response = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        self.assertContains(response, "All available donors with a compatible blood type")

    def test_donors_cannot_create_targeted_requests(self):
        self.client.force_login(self.other)

        response = self.client.get(self.url, {"donor": self.dina.pk})

        self.assertEqual(response.status_code, 403)
