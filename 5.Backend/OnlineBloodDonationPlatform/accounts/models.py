from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        DONOR = "DONOR", "Donor"
        HOSPITAL = "HOSPITAL", "Hospital"
        ADMIN = "ADMIN", "Admin"

    class BloodType(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"

    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    blood_type = models.CharField(
        max_length=3, choices=BloodType.choices, blank=True, default=""
    )
    is_available = models.BooleanField(default=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.DONOR
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Donation(models.Model):
    donor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="donations"
    )
    donation_date = models.DateField()
    blood_type = models.CharField(
        max_length=3, choices=User.BloodType.choices
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-donation_date"]

    def __str__(self):
        return f"{self.donor.get_full_name()} - {self.donation_date}"


class BloodRequest(models.Model):
    class Urgency(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine"
        URGENT = "URGENT", "Urgent"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_REVIEW = "IN_REVIEW", "In Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    hospital = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blood_requests",
        limit_choices_to={"role": User.Role.HOSPITAL},
    )
    blood_type = models.CharField(
        max_length=3, choices=User.BloodType.choices
    )
    units_needed = models.PositiveIntegerField(default=1)
    urgency = models.CharField(
        max_length=20, choices=Urgency.choices, default=Urgency.ROUTINE
    )
    notes = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.hospital.get_full_name()} - "
            f"{self.blood_type} ({self.urgency})"
        )

    def clean(self):
        # ValidationError (not ValueError) so forms and the admin show the
        # message next to the field instead of crashing with a 500 error.
        errors = {}

        if self.units_needed is not None and self.units_needed <= 0:
            errors["units_needed"] = "Units needed must be greater than 0."

        if self.urgency in {self.Urgency.URGENT, self.Urgency.EMERGENCY} and not self.notes.strip():
            errors["notes"] = "Please add notes for urgent or emergency requests."

        if errors:
            raise ValidationError(errors)

    def can_transition_to(self, new_status):
        allowed = {
            self.Status.OPEN: {
                self.Status.IN_REVIEW,
                self.Status.CANCELLED,
                self.Status.COMPLETED,
            },
            self.Status.IN_REVIEW: {
                self.Status.ACCEPTED,
                self.Status.CANCELLED,
                self.Status.COMPLETED,
            },
            self.Status.ACCEPTED: {self.Status.COMPLETED},
            self.Status.COMPLETED: set(),
            self.Status.CANCELLED: set(),
        }
        return new_status in allowed.get(self.status, set())

    def update_status(self, new_status):
        if not self.can_transition_to(new_status):
            raise ValidationError("This status change is not allowed.")
        self.status = new_status
        self.save(update_fields=["status"])

    # Donors can answer (and change their answer) until the request closes.
    CLOSED_STATUSES = (Status.COMPLETED, Status.CANCELLED)

    @property
    def is_closed(self):
        return self.status in self.CLOSED_STATUSES

    @property
    def accepted_responses_count(self):
        return self.responses.filter(response="ACCEPTED").count()

    @property
    def new_accepted_responses_count(self):
        """Accepted answers the hospital hasn't seen yet."""
        return self.responses.filter(response="ACCEPTED", seen_by_hospital=False).count()


class DonorResponse(models.Model):
    """
    A donor's answer to a blood request (#012). One per donor per request;
    the donor can change it until the request is completed or cancelled.
    The request's status is still changed by the hospital only.
    """

    class Answer(models.TextChoices):
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"

    blood_request = models.ForeignKey(
        BloodRequest, on_delete=models.CASCADE, related_name="responses",
    )
    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="request_responses",
        limit_choices_to={"role": User.Role.DONOR},
    )
    response = models.CharField(max_length=10, choices=Answer.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    # Changes when the donor changes their answer.
    updated_at = models.DateTimeField(auto_now=True)
    # False until the hospital opens the request after this answer; drives
    # the hospital's "new accepted responses" badge. Reset on every change.
    seen_by_hospital = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["blood_request", "donor"],
                name="one_response_per_donor_per_request",
            ),
        ]

    def __str__(self):
        return f"{self.donor.email} - {self.get_response_display()} ({self.blood_request_id})"

    @property
    def shares_contact(self):
        """Contact details are exchanged only while the answer is Accepted."""
        return self.response == self.Answer.ACCEPTED
