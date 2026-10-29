"""#015: donors add, edit and delete their own donation records."""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import BloodRequest, Donation, DonorResponse, User


PASSWORD = "StrongPass123!"


class DonationTests(TestCase):

    def setUp(self):
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, first_name="Dina", role="DONOR", blood_type="O-",
        )
        self.other_donor = User.objects.create_user(
            email="omar@example.com", password=PASSWORD, first_name="Omar", role="DONOR", blood_type="A+",
        )
        self.client.force_login(self.donor)
        self.url = reverse("donation_history")

    def add(self, **data):
        payload = {"donation_date": "2026-05-01", "place": "Kabul Blood Bank", "notes": "Felt fine"}
        payload.update(data)
        return self.client.post(self.url, payload, follow=True)

    def test_add_donation_uses_profile_blood_type(self):
        response = self.add()

        donation = Donation.objects.get()
        self.assertEqual(donation.donor, self.donor)
        self.assertEqual(donation.blood_type, "O-")
        self.assertEqual(donation.place, "Kabul Blood Bank")
        self.assertContains(response, "Your donation has been added")
        self.assertContains(response, "Kabul Blood Bank")

    def test_blood_type_in_post_is_ignored(self):
        self.add(blood_type="AB+")

        self.assertEqual(Donation.objects.get().blood_type, "O-")

    def test_future_dates_are_refused(self):
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)

        response = self.add(donation_date=tomorrow.isoformat())

        self.assertFalse(Donation.objects.exists())
        self.assertContains(response, "can&#x27;t be in the future")

    def test_date_is_required(self):
        self.add(donation_date="")

        self.assertFalse(Donation.objects.exists())

    def test_donor_without_blood_type_must_set_it_first(self):
        self.donor.blood_type = ""
        self.donor.save()

        response = self.add()

        self.assertFalse(Donation.objects.exists())
        self.assertContains(response, "Add your blood type")

    def test_history_is_newest_first(self):
        self.add(donation_date="2026-01-10", place="First")
        self.add(donation_date="2026-06-20", place="Second")

        html = self.client.get(self.url).content.decode()

        self.assertLess(html.index("Second"), html.index("First"))

    def test_edit_own_donation(self):
        self.add()
        donation = Donation.objects.get()

        response = self.client.post(
            reverse("edit_donation", args=[donation.pk]),
            {"donation_date": "2026-04-02", "place": "Herat Hospital", "notes": ""},
            follow=True,
        )

        donation.refresh_from_db()
        self.assertEqual(donation.place, "Herat Hospital")
        self.assertEqual(donation.donation_date, datetime.date(2026, 4, 2))
        self.assertContains(response, "has been updated")

    def test_delete_own_donation_needs_post(self):
        self.add()
        donation = Donation.objects.get()
        url = reverse("delete_donation", args=[donation.pk])

        self.assertContains(self.client.get(url), "Delete this donation?")
        self.assertTrue(Donation.objects.exists())

        self.client.post(url)
        self.assertFalse(Donation.objects.exists())

    def test_cannot_edit_or_delete_someone_elses_donation(self):
        theirs = Donation.objects.create(
            donor=self.other_donor, donation_date=datetime.date(2026, 3, 1), blood_type="A+",
        )

        for name in ("edit_donation", "delete_donation"):
            with self.subTest(view=name):
                url = reverse(name, args=[theirs.pk])
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {"donation_date": "2026-01-01"}).status_code, 404)
        self.assertTrue(Donation.objects.filter(pk=theirs.pk).exists())

    def test_history_is_private(self):
        Donation.objects.create(
            donor=self.other_donor, donation_date=datetime.date(2026, 3, 1), blood_type="A+", place="Secret place",
        )

        self.assertNotContains(self.client.get(self.url), "Secret place")

    def test_other_roles_get_403(self):
        hospital = User.objects.create_user(email="h@example.com", password=PASSWORD, first_name="H", role="HOSPITAL")
        self.client.force_login(hospital)

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, {"donation_date": "2026-01-01"}).status_code, 403)


class SuggestFromCompletedRequestTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="h@example.com", password=PASSWORD, first_name="Ali Abad", last_name="Hospital", role="HOSPITAL",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, first_name="Dina", role="DONOR", blood_type="O-",
        )
        self.blood_request = BloodRequest.objects.create(
            hospital=self.hospital, blood_type="A+", status=BloodRequest.Status.COMPLETED,
        )
        DonorResponse.objects.create(blood_request=self.blood_request, donor=self.donor, response="ACCEPTED")
        self.client.force_login(self.donor)
        self.url = reverse("donation_history")

    def test_completed_accepted_request_is_suggested_and_prefills(self):
        page = self.client.get(self.url)
        self.assertContains(page, "Add this donation")

        prefilled = self.client.get(self.url, {"request": self.blood_request.pk})
        self.assertEqual(prefilled.context["form"].initial["place"], "Ali Abad Hospital")

        self.client.post(self.url, {
            "donation_date": timezone.localdate().isoformat(), "place": "Ali Abad Hospital",
            "blood_request": self.blood_request.pk,
        })

        self.assertEqual(Donation.objects.get().blood_request, self.blood_request)
        self.assertNotContains(self.client.get(self.url), "Add this donation")

    def test_declined_or_open_requests_are_not_suggested(self):
        DonorResponse.objects.filter(donor=self.donor).update(response="DECLINED")
        self.assertNotContains(self.client.get(self.url), "Add this donation")

        DonorResponse.objects.filter(donor=self.donor).update(response="ACCEPTED")
        BloodRequest.objects.filter(pk=self.blood_request.pk).update(status=BloodRequest.Status.ACCEPTED)
        self.assertNotContains(self.client.get(self.url), "Add this donation")

    def test_cannot_link_a_request_that_is_not_yours(self):
        other_request = BloodRequest.objects.create(
            hospital=self.hospital, blood_type="A+", status=BloodRequest.Status.COMPLETED,
        )

        self.client.post(self.url, {"donation_date": "2026-01-01", "blood_request": other_request.pk})

        self.assertIsNone(Donation.objects.get().blood_request)
