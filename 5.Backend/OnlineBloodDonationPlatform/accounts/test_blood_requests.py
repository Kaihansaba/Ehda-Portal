from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import BloodRequest, User


class BloodRequestValidationTests(TestCase):
    """Regression tests for the BloodRequest.clean() ValueError fix."""

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com",
            password="StrongPass123!",
            first_name="City",
            role="HOSPITAL",
        )

    def test_model_clean_raises_validation_error_not_value_error(self):
        request = BloodRequest(
            hospital=self.hospital,
            blood_type="A-",
            units_needed=2,
            urgency=BloodRequest.Urgency.EMERGENCY,
            notes="",
        )

        with self.assertRaises(ValidationError) as caught:
            request.full_clean()

        self.assertIn("notes", caught.exception.message_dict)

    def test_urgent_request_without_notes_shows_one_error(self):
        self.client.force_login(self.hospital)

        response = self.client.post(
            reverse("create_blood_request"),
            {"blood_type": "A-", "units_needed": 2, "urgency": "URGENT", "notes": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["form"].errors["notes"]), 1)
        self.assertFalse(BloodRequest.objects.exists())
