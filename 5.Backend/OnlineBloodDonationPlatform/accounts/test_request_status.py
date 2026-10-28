from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, User


PASSWORD = "StrongPass123!"
Status = BloodRequest.Status


class BloodRequestTransitionTests(TestCase):
    """BloodRequest.can_transition_to / update_status (Shafiqa's Sprint 3)."""

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="City", role="HOSPITAL",
        )

    def make(self, status):
        return BloodRequest.objects.create(
            hospital=self.hospital, blood_type="O+", notes="Patient care.", status=status,
        )

    def test_allowed_changes(self):
        allowed = {
            Status.OPEN: {Status.IN_REVIEW, Status.CANCELLED, Status.COMPLETED},
            Status.IN_REVIEW: {Status.ACCEPTED, Status.CANCELLED, Status.COMPLETED},
            Status.ACCEPTED: {Status.COMPLETED},
            Status.COMPLETED: set(),
            Status.CANCELLED: set(),
        }

        for current, targets in allowed.items():
            blood_request = BloodRequest(status=current)
            for target in Status.values:
                with self.subTest(current=current, target=target):
                    self.assertEqual(blood_request.can_transition_to(target), target in targets)

    def test_update_status_saves(self):
        blood_request = self.make(Status.OPEN)

        blood_request.update_status(Status.IN_REVIEW)

        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.IN_REVIEW)

    def test_update_status_rejects_invalid_change(self):
        blood_request = self.make(Status.COMPLETED)

        with self.assertRaises(ValidationError):
            blood_request.update_status(Status.OPEN)

        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.COMPLETED)


class RequestStatusViewTests(TestCase):
    """Hospital status buttons and the request detail page."""

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="City", role="HOSPITAL",
        )
        self.other_hospital = User.objects.create_user(
            email="other@example.com", password=PASSWORD, first_name="Other", role="HOSPITAL",
        )
        self.client.force_login(self.hospital)

    def make(self, status=Status.OPEN, hospital=None, **fields):
        fields.setdefault("blood_type", "O+")
        fields.setdefault("notes", "Need blood for patient.")
        return BloodRequest.objects.create(
            hospital=hospital or self.hospital, status=status, **fields,
        )

    def change(self, blood_request, status):
        return self.client.post(
            reverse("change_request_status", args=[blood_request.pk, status])
        )

    def close(self, blood_request, status, **kwargs):
        return self.client.post(
            reverse("close_blood_request", args=[blood_request.pk]), {"status": status}, **kwargs
        )

    def test_hospital_can_move_request_to_in_review(self):
        blood_request = self.make(Status.OPEN)

        response = self.change(blood_request, "IN_REVIEW")

        self.assertRedirects(response, reverse("manage_blood_requests"))
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.IN_REVIEW)

    def test_hospital_can_accept_request(self):
        blood_request = self.make(Status.IN_REVIEW, blood_type="A-", urgency="URGENT")

        response = self.change(blood_request, "ACCEPTED")

        self.assertRedirects(response, reverse("manage_blood_requests"))
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.ACCEPTED)

    def test_hospital_can_cancel_request(self):
        blood_request = self.make(Status.OPEN)

        response = self.change(blood_request, "CANCELLED")

        self.assertRedirects(response, reverse("manage_blood_requests"))
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.CANCELLED)

    def test_hospital_can_close_a_blood_request(self):
        blood_request = self.make(Status.ACCEPTED)

        response = self.close(blood_request, "COMPLETED", follow=True)

        self.assertRedirects(response, reverse("manage_blood_requests"))
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.COMPLETED)

    def test_hospital_cannot_cancel_accepted_request(self):
        blood_request = self.make(Status.ACCEPTED)

        response = self.close(blood_request, "CANCELLED")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This status change is not allowed.")
        # The message is shown as text, not as a Python list.
        self.assertNotContains(response, "[&#x27;")
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.ACCEPTED)

    def test_unknown_status_in_url_shows_error(self):
        blood_request = self.make(Status.OPEN)

        response = self.change(blood_request, "DELETED")

        self.assertContains(response, "This status change is not allowed.")
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.OPEN)

    def test_close_ignores_other_statuses(self):
        blood_request = self.make(Status.OPEN)

        response = self.close(blood_request, "ACCEPTED")

        self.assertRedirects(response, reverse("manage_blood_requests"))
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.OPEN)

    def test_get_does_not_change_status(self):
        blood_request = self.make(Status.OPEN)

        for url in (
            reverse("change_request_status", args=[blood_request.pk, "IN_REVIEW"]),
            reverse("close_blood_request", args=[blood_request.pk]),
        ):
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), reverse("manage_blood_requests"))

        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, Status.OPEN)

    def test_cannot_touch_another_hospitals_request(self):
        theirs = self.make(Status.OPEN, hospital=self.other_hospital)

        self.assertEqual(self.change(theirs, "IN_REVIEW").status_code, 404)
        self.assertEqual(self.close(theirs, "CANCELLED").status_code, 404)
        self.assertEqual(
            self.client.get(reverse("request_detail", args=[theirs.pk])).status_code, 404
        )
        theirs.refresh_from_db()
        self.assertEqual(theirs.status, Status.OPEN)

    def test_list_shows_buttons_for_each_status(self):
        open_request = self.make(Status.OPEN)
        review_request = self.make(Status.IN_REVIEW)
        accepted_request = self.make(Status.ACCEPTED)

        response = self.client.get(reverse("manage_blood_requests"))

        self.assertContains(response, reverse("change_request_status", args=[open_request.pk, "IN_REVIEW"]))
        self.assertContains(response, reverse("change_request_status", args=[review_request.pk, "ACCEPTED"]))
        self.assertContains(response, reverse("close_blood_request", args=[accepted_request.pk]))
        self.assertContains(response, reverse("request_detail", args=[open_request.pk]))

    def test_detail_page(self):
        blood_request = self.make(Status.OPEN, units_needed=3, notes="Car accident, theatre 2.")

        response = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["blood_request"], blood_request)
        self.assertContains(response, "Car accident, theatre 2.")
        self.assertContains(response, "Mark in review")
        # Django's request object is not hidden: the navbar still shows the user.
        self.assertContains(response, reverse("logout"))

    def test_detail_page_for_finished_request_has_no_buttons(self):
        blood_request = self.make(Status.COMPLETED)

        response = self.client.get(reverse("request_detail", args=[blood_request.pk]))

        self.assertContains(response, "can no longer be changed")
        self.assertNotContains(response, reverse("close_blood_request", args=[blood_request.pk]))
