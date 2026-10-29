"""#011: in-app notifications, also sent by email."""
from decimal import Decimal
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, Notification, User
from locations.models import DonorLocation


PASSWORD = "StrongPass123!"


class NotificationTestCase(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL", phone="0700111222",
        )
        self.donor = self.make_donor("dina@example.com", "O-", "Dina", "Donoryan")
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")

    def make_donor(self, email, blood_type, first_name="Don", last_name="Or", **extra):
        donor = User.objects.create_user(
            email=email, password=PASSWORD, role="DONOR", blood_type=blood_type,
            first_name=first_name, last_name=last_name, phone="0799888777", **extra,
        )
        DonorLocation.objects.create(
            user=donor, province="Kabul", latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )
        return donor

    def create_request(self, **data):
        self.client.force_login(self.hospital)
        payload = {"blood_type": "A+", "units_needed": 2, "urgency": "ROUTINE", "notes": ""}
        payload.update(data)
        self.client.post(reverse("create_blood_request"), payload)
        return BloodRequest.objects.latest("pk")


class TriggerTests(NotificationTestCase):

    def test_matching_donors_are_notified_of_a_new_request(self):
        incompatible = self.make_donor("ab@example.com", "AB+")
        unavailable = self.make_donor("busy@example.com", "O-", is_available=False)

        self.create_request()

        note = Notification.objects.get(user=self.donor)
        self.assertIn("Ali Abad Hospital needs 2 units of A+", note.message)
        self.assertEqual(note.link, reverse("donor_blood_requests"))
        self.assertFalse(Notification.objects.filter(user__in=[incompatible, unavailable]).exists())
        self.assertEqual([m.to for m in mail.outbox], [[self.donor.email]])

    def test_only_the_target_donor_is_notified_of_a_targeted_request(self):
        other = self.make_donor("other@example.com", "O-")

        self.create_request(target_donor=self.donor.pk)

        self.assertIn("sent to you", Notification.objects.get(user=self.donor).message)
        self.assertFalse(Notification.objects.filter(user=other).exists())

    def test_hospital_is_notified_of_accept_and_decline(self):
        blood_request = self.create_request()
        self.client.force_login(self.donor)
        url = reverse("respond_to_request", args=[blood_request.pk])

        self.client.post(url, {"response": "ACCEPTED"})
        self.client.post(url, {"response": "ACCEPTED"})  # same answer again: no new notification
        self.client.post(url, {"response": "DECLINED"})

        messages = list(Notification.objects.filter(user=self.hospital).values_list("message", flat=True))
        self.assertEqual(messages, [
            "Dina D. declined your request for 2 units of A+.",
            "Dina D. accepted your request for 2 units of A+.",
        ])
        self.assertTrue(all("Donoryan" not in m for m in messages))

    def test_donors_involved_are_notified_of_status_changes(self):
        blood_request = self.create_request()
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="ACCEPTED")
        bystander = self.make_donor("bystander@example.com", "O+")
        Notification.objects.all().delete()

        self.client.force_login(self.hospital)
        self.client.post(reverse("change_request_status", args=[blood_request.pk, "IN_REVIEW"]))
        self.client.post(reverse("close_blood_request", args=[blood_request.pk]), {"status": "CANCELLED"})

        messages = list(Notification.objects.filter(user=self.donor).values_list("message", flat=True))
        self.assertEqual(len(messages), 2)
        self.assertIn("is now Cancelled", messages[0])
        self.assertIn("is now In Review", messages[1])
        self.assertFalse(Notification.objects.filter(user=bystander).exists())

    def test_refused_status_change_notifies_nobody(self):
        blood_request = self.create_request()
        DonorResponse.objects.create(blood_request=blood_request, donor=self.donor, response="ACCEPTED")
        Notification.objects.all().delete()

        self.client.post(reverse("change_request_status", args=[blood_request.pk, "ACCEPTED"]))  # Open -> Accepted not allowed

        self.assertFalse(Notification.objects.exists())

    def test_account_deactivation_and_reactivation(self):
        self.client.force_login(self.admin_user)
        url = reverse("toggle_user_status", args=[self.donor.pk])

        self.client.post(url)
        self.client.post(url)

        messages = list(Notification.objects.filter(user=self.donor).values_list("message", flat=True))
        self.assertIn("deactivated", messages[1])
        self.assertIn("reactivated", messages[0])
        self.assertEqual(len(mail.outbox), 2)


class EmailTests(NotificationTestCase):

    def test_email_contains_a_full_link(self):
        self.create_request()

        self.assertIn("http://testserver/dashboard/donor/requests/", mail.outbox[0].body)

    def test_email_failure_never_breaks_the_page(self):
        with mock.patch("accounts.notifications.send_mail", side_effect=OSError("SMTP down")):
            with self.assertLogs("accounts.notifications", level="ERROR"):
                blood_request = self.create_request()

        self.assertTrue(BloodRequest.objects.filter(pk=blood_request.pk).exists())
        self.assertTrue(Notification.objects.filter(user=self.donor).exists())


class NotificationPageTests(NotificationTestCase):

    def setUp(self):
        super().setUp()
        self.first = Notification.objects.create(user=self.donor, message="First", link="/dashboard/donor/requests/")
        self.second = Notification.objects.create(user=self.donor, message="Second")
        Notification.objects.create(user=self.hospital, message="Not yours")
        self.client.force_login(self.donor)

    def test_bell_shows_unread_count(self):
        response = self.client.get(reverse("donor_dashboard"))

        self.assertEqual(response.context["unread_notification_count"], 2)
        self.assertContains(response, "(2 unread)")

    def test_page_lists_only_own_notifications(self):
        response = self.client.get(reverse("notifications"))

        self.assertContains(response, "First")
        self.assertContains(response, "Second")
        self.assertNotContains(response, "Not yours")

    def test_opening_marks_read_and_follows_link(self):
        response = self.client.get(reverse("open_notification", args=[self.first.pk]))

        self.assertRedirects(response, "/dashboard/donor/requests/")
        self.first.refresh_from_db()
        self.assertTrue(self.first.read)

    def test_external_links_are_never_followed(self):
        for link in ("https://evil.example.com/", "//evil.example.com", "/\\\\evil.example.com"):
            with self.subTest(link=link):
                note = Notification.objects.create(user=self.donor, message="x", link=link)
                response = self.client.get(reverse("open_notification", args=[note.pk]))
                self.assertRedirects(response, reverse("notifications"))

    def test_cannot_open_someone_elses_notification(self):
        theirs = Notification.objects.get(message="Not yours")

        response = self.client.get(reverse("open_notification", args=[theirs.pk]))

        self.assertEqual(response.status_code, 404)
        theirs.refresh_from_db()
        self.assertFalse(theirs.read)

    def test_mark_all_as_read(self):
        response = self.client.post(reverse("mark_all_notifications_read"), follow=True)

        self.assertContains(response, "All notifications are marked as read.")
        self.assertFalse(self.donor.notifications.filter(read=False).exists())
        self.assertEqual(response.context["unread_notification_count"], 0)
        self.assertTrue(Notification.objects.filter(message="Not yours", read=False).exists())

    def test_get_does_not_mark_all_read(self):
        self.client.get(reverse("mark_all_notifications_read"))

        self.assertEqual(self.donor.notifications.filter(read=False).count(), 2)
