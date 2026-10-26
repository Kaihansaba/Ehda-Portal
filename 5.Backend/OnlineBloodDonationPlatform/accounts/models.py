
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
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

    email = models.EmailField(
        unique=True,
        max_length=254
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    blood_type = models.CharField(
        max_length=3,
        choices=BloodType.choices,
        blank=True,
        default=""
    )

    is_available = models.BooleanField(
        default=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DONOR
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
        max_length=3,
        choices=User.BloodType.choices,
    )
    units_needed = models.PositiveIntegerField(default=1)
    urgency = models.CharField(
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.ROUTINE,
    )
    notes = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.hospital.get_full_name()} - {self.blood_type} ({self.urgency})"

    def clean(self):
        if self.units_needed <= 0:
            raise ValueError("Units needed must be greater than 0.")

        if self.urgency in {self.Urgency.URGENT, self.Urgency.EMERGENCY} and not self.notes.strip():
            raise ValueError("Please add notes for urgent or emergency requests.")
