"""Donor side of blood requests: #011 (notification), #012 (answer), #013 (hospital sees it)."""
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from accounts.donor_requests import recipient_types_for, requests_for_donor, unanswered_count
from accounts.models import BloodRequest, DonorResponse, User
from locations.models import DonorLocation


PASSWORD = "StrongPass123!"
Status = BloodRequest.Status


class DonorRequestsTestCase(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD,
            first_name="Ali Abad", last_name="Hospital", role="HOSPITAL", phone="0700111222",
        )
        self.other_hospital = User.objects.create_user(
            email="other-hospital@example.com", password=PASSWORD,
            first_name="Other", last_name="Hospital", role="HOSPITAL",
        )
        self.donor = self.make_donor("dina@example.com", "O-", first_name="Dina", last_name="Donoryan")
        DonorLocation.objects.create(
            user=self.donor, province="Kabul",
            latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )

    def make_donor(self, email, blood_type, **fields):
        fields.setdefault("first_name", "Don")
        fields.setdefault("last_name", "Or")
        fields.setdefault("phone", "0799888777")
        return User.objects.create_user(
            email=email, password=PASSWORD, role="DONOR", blood_type=blood_type, **fields,
        )

    def make_request(self, blood_type="A+", status=Status.OPEN, hospital=None, **fields):
        fields.setdefault("notes", "Needed for surgery.")
        return BloodRequest.objects.create(
            hospital=hospital or self.hospital, blood_type=blood_type, status=status, **fields,
        )

    def respond(self, blood_request, answer, **kwargs):
        return self.client.post(
            reverse("respond_to_request", args=[blood_request.pk]), {"response": answer}, **kwargs
        )


class MatchingTests(DonorRequestsTestCase):

    def test_recipient_types_follow_the_compatibility_table(self):
        self.assertCountEqual(recipient_types_for("O-"), ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"])
        self.assertCountEqual(recipient_types_for("AB+"), ["AB+"])
        self.assertCountEqual(recipient_types_for("A-"), ["A-", "A+", "AB-", "AB+"])

    def test_donor_sees_only_requests_they_can_give_to(self):
        a_pos = self.make_request("A+")
        b_neg = self.make_request("B-")
        donor = self.make_donor("a-neg@example.com", "A-")

        self.assertEqual(list(requests_for_donor(donor)), [a_pos])
        self.assertIn(b_neg, requests_for_donor(self.donor))  # O- gives to everyone

    def test_only_open_or_in_review_requests_are_listed(self):
        open_request = self.make_request(status=Status.OPEN)
        review_request = self.make_request(status=Status.IN_REVIEW)
        for status in (Status.ACCEPTED, Status.COMPLETED, Status.CANCELLED):
            self.make_request(status=status)

        self.assertCountEqual(requests_for_donor(self.donor), [open_request, review_request])

    def test_answered_request_stays_listed_until_closed(self):
        blood_request = self.make_request()
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="ACCEPTED")

        blood_request.update_status(Status.IN_REVIEW)
        blood_request.update_status(Status.ACCEPTED)
        self.assertIn(blood_request, requests_for_donor(self.donor))

        blood_request.update_status(Status.COMPLETED)
        self.assertNotIn(blood_request, requests_for_donor(self.donor))

    def test_unavailable_donor_sees_none(self):
        self.make_request()
        self.donor.is_available = False
        self.donor.save()

        self.assertEqual(list(requests_for_donor(self.donor)), [])
        self.assertEqual(unanswered_count(self.donor), 0)

        self.client.force_login(self.donor)
        response = self.client.get(reverse("donor_blood_requests"))
        self.assertContains(response, "You’re marked as not available")
        self.assertContains(response, reverse("donor_dashboard"))
        self.assertNotContains(response, "Needed for surgery.")

    def test_donor_without_blood_type_sees_none(self):
        self.make_request()
        donor = self.make_donor("no-type@example.com", "")
        self.client.force_login(donor)

        response = self.client.get(reverse("donor_blood_requests"))

        self.assertContains(response, "Add your blood type first")
        self.assertEqual(response.context["blood_requests"], [])


class DonorPageTests(DonorRequestsTestCase):

    def test_page_shows_request_details_and_own_response(self):
        blood_request = self.make_request("AB+", urgency="URGENT", notes="Theatre 2, tonight.", units_needed=3)
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="DECLINED")
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_blood_requests"))

        self.assertContains(response, "Ali Abad Hospital")
        self.assertContains(response, "3 units of AB+")
        self.assertContains(response, "Urgent")
        self.assertContains(response, "Theatre 2, tonight.")
        self.assertContains(response, "You declined")
        self.assertContains(response, "Accept instead")
        self.assertNotContains(response, "Decline instead")

    def test_empty_state(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_blood_requests"))

        self.assertContains(response, "No requests for your blood type right now")

    def test_page_does_not_show_hospital_contact_details(self):
        self.make_request()
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_blood_requests"))

        self.assertNotContains(response, self.hospital.email)
        self.assertNotContains(response, self.hospital.phone)


class RespondTests(DonorRequestsTestCase):

    def setUp(self):
        super().setUp()
        self.blood_request = self.make_request()
        self.client.force_login(self.donor)

    def test_accept(self):
        response = self.respond(self.blood_request, "ACCEPTED")

        self.assertRedirects(response, reverse("donor_blood_requests"))
        saved = DonorResponse.objects.get(blood_request=self.blood_request, donor=self.donor)
        self.assertEqual(saved.response, "ACCEPTED")

    def test_decline(self):
        self.respond(self.blood_request, "DECLINED")

        saved = DonorResponse.objects.get(blood_request=self.blood_request, donor=self.donor)
        self.assertEqual(saved.response, "DECLINED")

    def test_change_response_keeps_one_row(self):
        self.respond(self.blood_request, "ACCEPTED")
        self.respond(self.blood_request, "DECLINED")
        self.respond(self.blood_request, "ACCEPTED")

        responses = DonorResponse.objects.filter(blood_request=self.blood_request, donor=self.donor)
        self.assertEqual(responses.count(), 1)
        self.assertEqual(responses.get().response, "ACCEPTED")

    def test_answer_does_not_change_request_status(self):
        self.respond(self.blood_request, "ACCEPTED")

        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, Status.OPEN)

    def test_closed_requests_cannot_be_answered(self):
        for status in (Status.COMPLETED, Status.CANCELLED):
            with self.subTest(status=status):
                closed = self.make_request(status=status)
                response = self.respond(closed, "ACCEPTED", follow=True)

                self.assertContains(response, "closed and can no longer be answered")
                self.assertFalse(DonorResponse.objects.filter(blood_request=closed).exists())

    def test_existing_answer_cannot_be_changed_after_close(self):
        self.respond(self.blood_request, "ACCEPTED")
        self.blood_request.update_status(Status.CANCELLED)

        self.respond(self.blood_request, "DECLINED")

        saved = DonorResponse.objects.get(blood_request=self.blood_request, donor=self.donor)
        self.assertEqual(saved.response, "ACCEPTED")

    def test_incompatible_request_cannot_be_answered(self):
        donor = self.make_donor("ab-pos@example.com", "AB+")
        self.client.force_login(donor)

        response = self.respond(self.blood_request, "ACCEPTED", follow=True)  # A+ request

        self.assertContains(response, "You can&#x27;t answer this request.")
        self.assertFalse(DonorResponse.objects.filter(donor=donor).exists())

    def test_unavailable_donor_cannot_answer(self):
        self.donor.is_available = False
        self.donor.save()

        self.respond(self.blood_request, "ACCEPTED")

        self.assertFalse(DonorResponse.objects.exists())

    def test_invalid_answer(self):
        response = self.respond(self.blood_request, "MAYBE", follow=True)

        self.assertContains(response, "Please choose Accept or Decline.")
        self.assertFalse(DonorResponse.objects.exists())

    def test_get_does_not_answer(self):
        response = self.client.get(reverse("respond_to_request", args=[self.blood_request.pk]))

        self.assertRedirects(response, reverse("donor_blood_requests"))
        self.assertFalse(DonorResponse.objects.exists())

    def test_unknown_request_is_404(self):
        response = self.client.post(reverse("respond_to_request", args=[99999]), {"response": "ACCEPTED"})

        self.assertEqual(response.status_code, 404)

    def test_one_response_per_donor_per_request_in_the_database(self):
        DonorResponse.objects.create(blood_request=self.blood_request, donor=self.donor, response="ACCEPTED")

        with self.assertRaises(IntegrityError):
            DonorResponse.objects.create(blood_request=self.blood_request, donor=self.donor, response="DECLINED")

    def test_other_roles_get_403(self):
        admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")

        for user in (self.hospital, admin_user):
            self.client.force_login(user)
            with self.subTest(role=user.role):
                self.assertEqual(self.client.get(reverse("donor_blood_requests")).status_code, 403)
                self.assertEqual(self.respond(self.blood_request, "ACCEPTED").status_code, 403)

        self.assertFalse(DonorResponse.objects.exists())


class NotificationCountTests(DonorRequestsTestCase):

    def test_dashboard_and_navbar_count_unanswered_matching_requests(self):
        answered = self.make_request("A+")
        self.make_request("B+")
        self.make_request("O-", status=Status.COMPLETED)  # closed: not counted
        DonorResponse.objects.create(blood_request=answered, donor=self.donor, response="DECLINED")
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_dashboard"))

        self.assertEqual(response.context["donor_request_count"], 1)
        self.assertContains(response, '<span class="count-badge">1 new</span>', html=True)
        self.assertContains(response, "(1 new)")  # navbar, for screen readers
        self.assertNotContains(response, "Coming soon")

    def test_count_follows_compatibility(self):
        self.make_request("A+")
        self.make_request("A+")
        self.make_request("O-")

        self.assertEqual(unanswered_count(self.donor), 3)
        self.assertEqual(unanswered_count(self.make_donor("ab@example.com", "AB+")), 0)

    def test_no_badge_when_nothing_new(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("donor_dashboard"))

        self.assertEqual(response.context["donor_request_count"], 0)
        self.assertNotContains(response, "count-badge")

    def test_other_roles_get_no_count(self):
        self.make_request()
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("hospital_dashboard"))

        self.assertNotIn("donor_request_count", response.context)


class HospitalSeesResponsesTests(DonorRequestsTestCase):

    def setUp(self):
        super().setUp()
        self.blood_request = self.make_request()
        self.decliner = self.make_donor(
            "ahmad@example.com", "A+", first_name="Ahmad", last_name="Saba", phone="0788555444",
        )
        DonorResponse.objects.create(blood_request=self.blood_request, donor=self.donor, response="ACCEPTED")
        DonorResponse.objects.create(blood_request=self.blood_request, donor=self.decliner, response="DECLINED")
        self.client.force_login(self.hospital)

    def test_detail_page_lists_responses(self):
        response = self.client.get(reverse("request_detail", args=[self.blood_request.pk]))

        # Dina accepted: full name. Ahmad declined: first name + last initial.
        self.assertContains(response, "Dina Donoryan")
        self.assertContains(response, "Ahmad S.")
        self.assertNotContains(response, "Ahmad Saba")
        self.assertContains(response, "Accepted")
        self.assertContains(response, "Declined")

    def test_manage_page_shows_accepted_count(self):
        response = self.client.get(reverse("manage_blood_requests"))

        self.assertContains(response, "1 donor accepted")

    def test_privacy_no_email_location_or_decliner_contact(self):
        pages = (
            reverse("request_detail", args=[self.blood_request.pk]),
            reverse("manage_blood_requests"),
        )

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                for private in (
                    self.donor.email, self.decliner.email, self.decliner.phone,
                    "Saba", "34.531234", "69.171234", "34.53", "69.17",
                ):
                    self.assertNotContains(response, private)

    def test_manage_list_never_shows_contact_details(self):
        response = self.client.get(reverse("manage_blood_requests"))

        self.assertNotContains(response, self.donor.phone)
        self.assertNotContains(response, "Donoryan")

    def test_other_hospital_cannot_see_responses(self):
        self.client.force_login(self.other_hospital)

        response = self.client.get(reverse("request_detail", args=[self.blood_request.pk]))

        self.assertEqual(response.status_code, 404)
        list_response = self.client.get(reverse("manage_blood_requests"))
        self.assertNotContains(list_response, "Dina D.")
        self.assertNotContains(list_response, "donor accepted")

    def test_status_is_still_changed_by_the_hospital_with_her_rules(self):
        self.client.post(reverse("change_request_status", args=[self.blood_request.pk, "ACCEPTED"]))
        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, Status.OPEN)  # Open -> Accepted not allowed

        self.client.post(reverse("change_request_status", args=[self.blood_request.pk, "IN_REVIEW"]))
        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, Status.IN_REVIEW)


class AdminResponsesTests(DonorRequestsTestCase):

    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password=PASSWORD, first_name="Ada",
        )
        blood_request = self.make_request()
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="ACCEPTED")
        self.client.force_login(self.admin_user)

    def test_platform_activity_includes_responses(self):
        response = self.client.get(reverse("admin_platform_activity"))

        summary = response.context["summary"]
        self.assertEqual(summary["total_responses"], 1)
        self.assertEqual(summary["accepted_responses"], 1)
        self.assertEqual(summary["declined_responses"], 0)
        self.assertContains(response, "Donor responses")

    def test_django_admin_lists_responses(self):
        url = reverse("admin:accounts_donorresponse_changelist")

        response = self.client.get(url, {"q": "Dina"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cl"].result_count, 1)
