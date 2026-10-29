"""Contact details are exchanged only while a donor has accepted a request."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.donor_requests import new_acceptances_count
from accounts.models import BloodRequest, DonorResponse, User
from locations.models import DonorLocation


PASSWORD = "StrongPass123!"
Status = BloodRequest.Status
SHARED_NOTE = "Shared because the donor accepted"


class ContactTestCase(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD,
            first_name="Ali Abad", last_name="Hospital", role="HOSPITAL", phone="0700111222",
        )
        self.other_hospital = User.objects.create_user(
            email="other@example.com", password=PASSWORD,
            first_name="Other", last_name="Hospital", role="HOSPITAL", phone="0700999000",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, role="DONOR", blood_type="O-",
            first_name="Dina", last_name="Donoryan", phone="0799888777",
        )
        DonorLocation.objects.create(
            user=self.donor, province="Kabul",
            latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )
        self.blood_request = BloodRequest.objects.create(
            hospital=self.hospital, blood_type="A+", notes="Surgery.",
        )

    def respond(self, answer):
        self.client.force_login(self.donor)
        return self.client.post(
            reverse("respond_to_request", args=[self.blood_request.pk]), {"response": answer},
        )

    def hospital_detail(self, hospital=None):
        self.client.force_login(hospital or self.hospital)
        return self.client.get(reverse("request_detail", args=[self.blood_request.pk]))

    def donor_page(self):
        self.client.force_login(self.donor)
        return self.client.get(reverse("donor_blood_requests"))


class HospitalSeesDonorContactTests(ContactTestCase):

    def test_no_response_shares_nothing(self):
        response = self.hospital_detail()

        self.assertNotContains(response, self.donor.phone)
        self.assertNotContains(response, "Dina")
        self.assertNotContains(response, SHARED_NOTE)

    def test_accepted_shares_full_name_and_phone(self):
        self.respond("ACCEPTED")

        response = self.hospital_detail()

        self.assertContains(response, "Dina Donoryan")
        self.assertContains(response, f'href="tel:{self.donor.phone}"')
        self.assertContains(response, SHARED_NOTE)

    def test_declined_shares_first_name_and_initial_only(self):
        self.respond("DECLINED")

        response = self.hospital_detail()

        self.assertContains(response, "Dina D.")
        self.assertNotContains(response, "Donoryan")
        self.assertNotContains(response, self.donor.phone)
        self.assertNotContains(response, SHARED_NOTE)

    def test_switching_to_decline_hides_contact_again(self):
        self.respond("ACCEPTED")
        self.assertContains(self.hospital_detail(), self.donor.phone)

        self.respond("DECLINED")
        response = self.hospital_detail()

        self.assertNotContains(response, self.donor.phone)
        self.assertNotContains(response, "Donoryan")
        self.assertContains(response, "Dina D.")

    def test_email_and_location_are_never_shared(self):
        self.respond("ACCEPTED")

        response = self.hospital_detail()

        for private in (self.donor.email, "34.531234", "69.171234", "34.53", "69.17"):
            self.assertNotContains(response, private)

    def test_other_hospitals_see_nothing(self):
        self.respond("ACCEPTED")

        detail = self.hospital_detail(self.other_hospital)
        self.assertEqual(detail.status_code, 404)

        listing = self.client.get(reverse("manage_blood_requests"))
        dashboard = self.client.get(reverse("hospital_dashboard"))
        for response in (listing, dashboard):
            self.assertNotContains(response, self.donor.phone)
            self.assertNotContains(response, "Dina")
        self.assertEqual(dashboard.context["hospital_new_accepted_count"], 0)


class DonorSeesHospitalContactTests(ContactTestCase):

    def test_hospital_contact_hidden_before_accepting(self):
        response = self.donor_page()

        self.assertContains(response, "Ali Abad Hospital")
        self.assertNotContains(response, self.hospital.phone)

    def test_hospital_contact_shown_after_accepting(self):
        self.respond("ACCEPTED")

        response = self.donor_page()

        self.assertContains(response, f'href="tel:{self.hospital.phone}"')
        self.assertContains(response, "Contact Ali Abad Hospital")

    def test_hospital_contact_hidden_after_declining(self):
        self.respond("ACCEPTED")
        self.respond("DECLINED")

        response = self.donor_page()

        self.assertNotContains(response, self.hospital.phone)

    def test_hospital_without_phone_shows_email(self):
        self.hospital.phone = ""
        self.hospital.save()
        self.respond("ACCEPTED")

        response = self.donor_page()

        self.assertContains(response, f'href="mailto:{self.hospital.email}"')

    def test_other_requests_do_not_share_contact(self):
        BloodRequest.objects.create(hospital=self.other_hospital, blood_type="B+", notes="Other.")
        self.respond("ACCEPTED")  # accepts only Ali Abad's request

        response = self.donor_page()

        self.assertContains(response, self.hospital.phone)
        self.assertNotContains(response, self.other_hospital.phone)


class NewAcceptedBadgeTests(ContactTestCase):

    def badge_count(self):
        self.client.force_login(self.hospital)
        return self.client.get(reverse("hospital_dashboard")).context["hospital_new_accepted_count"]

    def test_badge_counts_new_acceptances(self):
        second_donor = User.objects.create_user(
            email="ahmad@example.com", password=PASSWORD, role="DONOR", blood_type="A+",
            first_name="Ahmad", last_name="Saba", phone="0788555444",
        )
        self.respond("ACCEPTED")
        DonorResponse.objects.create(blood_request=self.blood_request, donor=second_donor, response="DECLINED")

        self.assertEqual(self.badge_count(), 1)  # declines are not counted

        self.client.force_login(self.hospital)
        response = self.client.get(reverse("hospital_dashboard"))
        self.assertContains(response, '<span class="count-badge">1 new</span>', html=True)
        self.assertContains(response, "(1 new accepted)")  # navbar, for screen readers

    def test_opening_detail_marks_viewed(self):
        self.respond("ACCEPTED")

        detail = self.hospital_detail()
        self.assertContains(detail, '<span class="count-badge">New</span>', html=True)
        self.assertEqual(self.badge_count(), 0)

        # Still accepted and still shared; just no longer "new".
        detail = self.hospital_detail()
        self.assertNotContains(detail, '<span class="count-badge">New</span>', html=True)
        self.assertContains(detail, self.donor.phone)

    def test_list_page_does_not_mark_viewed(self):
        self.respond("ACCEPTED")
        self.client.force_login(self.hospital)

        listing = self.client.get(reverse("manage_blood_requests"))

        self.assertContains(listing, '<span class="count-badge">1 new</span>', html=True)
        self.assertEqual(self.badge_count(), 1)

    def test_accepting_again_after_declining_is_new_again(self):
        self.respond("ACCEPTED")
        self.hospital_detail()
        self.assertEqual(self.badge_count(), 0)

        self.respond("DECLINED")
        self.assertEqual(self.badge_count(), 0)

        self.respond("ACCEPTED")
        self.assertEqual(self.badge_count(), 1)

    def test_closed_requests_are_not_counted(self):
        self.respond("ACCEPTED")
        self.blood_request.update_status(Status.CANCELLED)

        self.assertEqual(self.badge_count(), 0)

    def test_another_hospital_opening_its_page_does_not_mark_viewed(self):
        self.respond("ACCEPTED")
        self.hospital_detail(self.other_hospital)  # 404

        self.assertEqual(new_acceptances_count(self.hospital), 1)

    def test_donors_and_admins_get_no_hospital_badge(self):
        self.respond("ACCEPTED")

        response = self.donor_page()

        self.assertNotIn("hospital_new_accepted_count", response.context)
