from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, User


PASSWORD = "StrongPass123!"
Status = BloodRequest.Status


class HospitalDashboardStatsTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="City", role="HOSPITAL",
        )
        self.other_hospital = User.objects.create_user(
            email="other@example.com", password=PASSWORD, first_name="Other", role="HOSPITAL",
        )
        self.donors = [
            User.objects.create_user(
                email=f"donor{i}@example.com", password=PASSWORD, first_name=f"Donor{i}",
                role="DONOR", blood_type="O-",
            )
            for i in range(3)
        ]
        self.client.force_login(self.hospital)

    def make_request(self, status=Status.OPEN, hospital=None):
        return BloodRequest.objects.create(
            hospital=hospital or self.hospital, blood_type="A+", notes="Surgery.", status=status,
        )

    def answer(self, blood_request, donor, response):
        return DonorResponse.objects.create(blood_request=blood_request, donor=donor, response=response)

    def stats(self):
        response = self.client.get(reverse("hospital_dashboard"))
        self.assertEqual(response.status_code, 200)
        return response

    def test_zero_when_nothing_yet(self):
        response = self.stats()

        self.assertEqual(response.context["active_requests"], 0)
        self.assertEqual(response.context["donors_connected"], 0)
        self.assertNotContains(response, '<div class="stat-value">—</div>', html=True)

    def test_active_counts_open_and_in_review_only(self):
        self.make_request(Status.OPEN)
        self.make_request(Status.OPEN)
        self.make_request(Status.IN_REVIEW)
        for status in (Status.ACCEPTED, Status.COMPLETED, Status.CANCELLED):
            self.make_request(status)

        response = self.stats()

        self.assertEqual(response.context["active_requests"], 3)
        self.assertContains(response, '<div class="stat-value">3</div>', html=True)

    def test_active_ignores_other_hospitals(self):
        self.make_request(hospital=self.other_hospital)

        self.assertEqual(self.stats().context["active_requests"], 0)

    def test_donors_connected_counts_each_donor_once(self):
        first, second = self.make_request(), self.make_request(Status.COMPLETED)
        self.answer(first, self.donors[0], "ACCEPTED")
        self.answer(second, self.donors[0], "ACCEPTED")  # same donor, two requests
        self.answer(first, self.donors[1], "ACCEPTED")

        self.assertEqual(self.stats().context["donors_connected"], 2)

    def test_declined_donors_are_not_connected(self):
        blood_request = self.make_request()
        self.answer(blood_request, self.donors[0], "DECLINED")
        switched = self.answer(blood_request, self.donors[1], "ACCEPTED")
        switched.response = "DECLINED"
        switched.save()

        self.assertEqual(self.stats().context["donors_connected"], 0)

    def test_donors_connected_ignores_other_hospitals(self):
        self.answer(self.make_request(hospital=self.other_hospital), self.donors[0], "ACCEPTED")

        self.assertEqual(self.stats().context["donors_connected"], 0)
