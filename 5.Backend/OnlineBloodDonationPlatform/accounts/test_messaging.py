"""#014: messages between a hospital and a donor after the donor accepts."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, DonorResponse, Message, Notification, User


PASSWORD = "StrongPass123!"


class MessagingTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD, first_name="Ali Abad",
            last_name="Hospital", role="HOSPITAL", phone="0700111222",
        )
        self.other_hospital = User.objects.create_user(
            email="other@example.com", password=PASSWORD, first_name="Other", role="HOSPITAL",
        )
        self.donor = User.objects.create_user(
            email="dina@example.com", password=PASSWORD, first_name="Dina", last_name="Donoryan",
            role="DONOR", blood_type="O-", phone="0799888777",
        )
        self.other_donor = User.objects.create_user(
            email="omar@example.com", password=PASSWORD, first_name="Omar", role="DONOR", blood_type="O-",
        )
        self.blood_request = BloodRequest.objects.create(hospital=self.hospital, blood_type="A+", units_needed=2)
        self.response = DonorResponse.objects.create(
            blood_request=self.blood_request, donor=self.donor, response="ACCEPTED",
        )
        self.url = reverse("conversation", args=[self.blood_request.pk, self.donor.pk])

    def send(self, user, body):
        self.client.force_login(user)
        return self.client.post(self.url, {"body": body}, follow=True)

    def test_both_sides_can_send_and_see_history_in_order(self):
        self.send(self.hospital, "Can you come at 10?")
        response = self.send(self.donor, "Yes, see you then.")

        self.assertEqual(
            list(Message.objects.values_list("body", flat=True)),
            ["Can you come at 10?", "Yes, see you then."],
        )
        html = response.content.decode()
        self.assertLess(html.index("Can you come at 10?"), html.index("Yes, see you then."))

        self.client.force_login(self.hospital)
        self.assertContains(self.client.get(self.url), "Yes, see you then.")

    def test_new_message_notifies_the_other_party(self):
        self.send(self.donor, "Hello")

        note = Notification.objects.get(user=self.hospital)
        self.assertEqual(note.message, "New message from Dina D. about the request for 2 units of A+.")
        self.assertEqual(note.link, self.url)
        self.assertFalse(Notification.objects.filter(user=self.donor).exists())

        self.send(self.hospital, "Hi Dina")
        self.assertIn("Ali Abad Hospital", Notification.objects.get(user=self.donor).message)

    def test_read_only_after_decline(self):
        self.send(self.donor, "Before declining")
        self.response.response = "DECLINED"
        self.response.save()

        response = self.send(self.hospital, "Still there?")

        self.assertEqual(Message.objects.count(), 1)
        self.assertContains(response, "The donor declined this request")
        self.assertContains(response, "Before declining")
        self.assertNotContains(response, 'name="body"')
        # Contact rule: name falls back to first name + initial.
        self.assertContains(response, "Messages with Dina D.")
        self.assertNotContains(response, "Donoryan")

    def test_read_only_when_request_closed(self):
        self.blood_request.update_status(BloodRequest.Status.CANCELLED)

        response = self.send(self.donor, "Hello?")

        self.assertFalse(Message.objects.exists())
        self.assertContains(response, "conversation is closed")

    def test_no_conversation_without_a_response(self):
        self.client.force_login(self.hospital)

        response = self.client.get(reverse("conversation", args=[self.blood_request.pk, self.other_donor.pk]))

        self.assertEqual(response.status_code, 404)

    def test_outsiders_get_404_and_cannot_post(self):
        for user in (self.other_hospital, self.other_donor):
            with self.subTest(user=user.email):
                self.client.force_login(user)
                self.assertEqual(self.client.get(self.url).status_code, 404)
                self.assertEqual(self.client.post(self.url, {"body": "hi"}).status_code, 404)
                messages_url = reverse("conversation_messages", args=[self.blood_request.pk, self.donor.pk])
                self.assertEqual(self.client.get(messages_url).status_code, 404)
        self.assertFalse(Message.objects.exists())

    def test_admins_get_403(self):
        admin_user = User.objects.create_superuser(email="admin@example.com", password=PASSWORD, first_name="Ada")
        self.client.force_login(admin_user)

        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_empty_and_too_long_messages_are_refused(self):
        self.send(self.donor, "   ")
        response = self.send(self.donor, "x" * 2001)

        self.assertFalse(Message.objects.exists())
        self.assertContains(response, "at most 2000 characters")

    def test_polling_fragment_returns_messages(self):
        self.send(self.hospital, "Ping")
        self.client.force_login(self.donor)

        response = self.client.get(reverse("conversation_messages", args=[self.blood_request.pk, self.donor.pk]))

        self.assertContains(response, "Ping")
        self.assertNotContains(response, "<html")

    def test_messages_are_escaped(self):
        self.send(self.donor, "<script>alert(1)</script>")

        response = self.client.get(self.url)

        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_message_buttons_on_request_pages(self):
        self.client.force_login(self.hospital)
        self.assertContains(self.client.get(reverse("request_detail", args=[self.blood_request.pk])), self.url)

        self.client.force_login(self.donor)
        # The donor page lists the request (O- donor can give to A+).
        self.assertContains(self.client.get(reverse("donor_blood_requests")), self.url)
