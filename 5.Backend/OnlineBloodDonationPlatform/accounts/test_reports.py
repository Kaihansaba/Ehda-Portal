"""#019: users report accounts; admins review them."""
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, Notification, Report, User


PASSWORD = "StrongPass123!"


class ReportTestCase(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, first_name="Dina", last_name="Donoryan",
            role="DONOR", blood_type="O-",
        )
        self.stranger = User.objects.create_user(
            email="stranger@example.com", password=PASSWORD, first_name="Sam", role="DONOR", blood_type="A+",
        )
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")
        self.blood_request = BloodRequest.objects.create(hospital=self.hospital, blood_type="A+")
        DonorResponse.objects.create(blood_request=self.blood_request, donor=self.donor, response="ACCEPTED")

    def report(self, reporter, reported, **data):
        self.client.force_login(reporter)
        payload = {"reason": "NO_SHOW", "details": "Didn't come to the appointment on Monday."}
        payload.update(data)
        return self.client.post(reverse("report_user", args=[reported.pk]), payload, follow=True)


class SubmitReportTests(ReportTestCase):

    def test_hospital_reports_a_donor_who_answered(self):
        response = self.report(self.hospital, self.donor)

        report = Report.objects.get()
        self.assertEqual((report.reporter, report.reported_user), (self.hospital, self.donor))
        self.assertEqual(report.status, Report.Status.OPEN)
        self.assertContains(response, "An administrator will review your report.")

    def test_donor_reports_the_hospital(self):
        self.report(self.donor, self.hospital, reason="PAYMENT", details="They asked me to pay 500 Afghani.")

        self.assertEqual(Report.objects.get().reported_user, self.hospital)

    def test_report_page_names_donors_by_first_name_and_initial(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("report_user", args=[self.donor.pk]))

        self.assertContains(response, "Report Dina D.")
        self.assertNotContains(response, "Donoryan")
        self.assertNotContains(response, self.donor.email)

    def test_admins_are_notified(self):
        self.report(self.hospital, self.donor)

        note = Notification.objects.get(user=self.admin_user)
        self.assertEqual(note.link, reverse("admin_reported_accounts"))
        self.assertIn(self.admin_user.email, [m.to[0] for m in mail.outbox])
        # The reported person isn't told.
        self.assertFalse(Notification.objects.filter(user=self.donor).exists())

    def test_cannot_report_someone_you_never_dealt_with(self):
        for reporter, reported in ((self.hospital, self.stranger), (self.donor, self.stranger), (self.donor, self.donor)):
            with self.subTest(reporter=reporter.email, reported=reported.email):
                response = self.report(reporter, reported)
                self.assertEqual(response.status_code, 404)
        self.assertFalse(Report.objects.exists())

    def test_cannot_report_admins_or_unknown_accounts(self):
        self.assertEqual(self.report(self.donor, self.admin_user).status_code, 404)
        self.client.force_login(self.donor)
        self.assertEqual(self.client.get(reverse("report_user", args=[99999])).status_code, 404)

    def test_messages_or_targeted_requests_count_as_dealing_with_someone(self):
        other = User.objects.create_user(email="o@example.com", password=PASSWORD, first_name="O", role="DONOR", blood_type="O-")
        BloodRequest.objects.create(hospital=self.hospital, blood_type="A+", target_donor=other)

        self.report(self.hospital, other)

        self.assertEqual(Report.objects.get().reported_user, other)

    def test_reason_has_no_blank_choice(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("report_user", args=[self.donor.pk]))

        self.assertNotContains(response, "Select an option")
        self.assertNotContains(response, 'value="" checked')

    def test_validation(self):
        response = self.report(self.hospital, self.donor, details="short")
        self.assertContains(response, "at least 10 characters")

        response = self.report(self.hospital, self.donor, reason="NOT_A_REASON")
        self.assertTrue(response.context["form"].errors.get("reason"))
        self.assertFalse(Report.objects.exists())

    def test_only_one_open_report_per_account(self):
        self.report(self.hospital, self.donor)
        response = self.report(self.hospital, self.donor)

        self.assertEqual(Report.objects.count(), 1)
        self.assertContains(response, "already have an open report")

    def test_next_must_be_a_site_path(self):
        self.client.force_login(self.hospital)
        url = reverse("report_user", args=[self.donor.pk])
        payload = {"reason": "OTHER", "details": "Something happened here."}

        response = self.client.post(url, {**payload, "next": "https://evil.example.com/"})
        self.assertRedirects(response, reverse("role_redirect"), fetch_redirect_response=False)

        detail = reverse("request_detail", args=[self.blood_request.pk])
        Report.objects.all().delete()
        response = self.client.post(url, {**payload, "next": detail})
        self.assertRedirects(response, detail)

    def test_admins_cannot_file_reports(self):
        self.client.force_login(self.admin_user)

        self.assertEqual(self.client.get(reverse("report_user", args=[self.donor.pk])).status_code, 403)

    def test_report_links_on_pages(self):
        self.client.force_login(self.hospital)
        detail = self.client.get(reverse("request_detail", args=[self.blood_request.pk]))
        self.assertContains(detail, reverse("report_user", args=[self.donor.pk]))

        self.client.force_login(self.donor)
        page = self.client.get(reverse("donor_blood_requests"))
        self.assertContains(page, reverse("report_user", args=[self.hospital.pk]))
        convo = self.client.get(reverse("conversation", args=[self.blood_request.pk, self.donor.pk]))
        self.assertContains(convo, reverse("report_user", args=[self.hospital.pk]))


class ReviewReportTests(ReportTestCase):

    def setUp(self):
        super().setUp()
        self.report(self.hospital, self.donor)
        self.the_report = Report.objects.get()
        self.client.force_login(self.admin_user)

    def review(self, action):
        return self.client.post(reverse("review_report", args=[self.the_report.pk]), {"action": action}, follow=True)

    def test_admin_page_lists_real_reports(self):
        response = self.client.get(reverse("admin_reported_accounts"))

        self.assertEqual(list(response.context["reports"]), [self.the_report])
        self.assertContains(response, "Didn&#x27;t come to the appointment")
        self.assertContains(response, self.donor.email)  # admins may see it

    def test_mark_reviewed(self):
        response = self.review("reviewed")

        self.the_report.refresh_from_db()
        self.assertEqual(self.the_report.status, Report.Status.REVIEWED)
        self.assertEqual(self.the_report.reviewed_by, self.admin_user)
        self.assertIsNotNone(self.the_report.reviewed_at)
        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_active)
        self.assertContains(response, "marked as reviewed")

    def test_deactivate_account(self):
        self.review("deactivate")

        self.the_report.refresh_from_db()
        self.donor.refresh_from_db()
        self.assertEqual(self.the_report.status, Report.Status.ACTION_TAKEN)
        self.assertFalse(self.donor.is_active)
        self.assertTrue(Notification.objects.filter(user=self.donor, message__contains="deactivated").exists())

    def test_dashboard_counts_open_reports(self):
        self.assertEqual(self.client.get(reverse("admin_dashboard")).context["open_report_count"], 1)
        self.review("reviewed")
        self.assertEqual(self.client.get(reverse("admin_dashboard")).context["open_report_count"], 0)

    def test_unknown_action_and_get_change_nothing(self):
        self.review("delete")
        self.client.get(reverse("review_report", args=[self.the_report.pk]))

        self.the_report.refresh_from_db()
        self.assertEqual(self.the_report.status, Report.Status.OPEN)

    def test_only_admins_can_review(self):
        for user in (self.hospital, self.donor):
            self.client.force_login(user)
            self.assertEqual(self.review("deactivate").status_code, 403)
            self.assertEqual(self.client.get(reverse("admin_reported_accounts")).status_code, 403)
        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_active)
