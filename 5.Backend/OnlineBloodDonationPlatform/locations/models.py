from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import PROVINCE_CHOICES
from .utils import approximate


LATITUDE_VALIDATORS = [MinValueValidator(-90), MaxValueValidator(90)]
LONGITUDE_VALIDATORS = [MinValueValidator(-180), MaxValueValidator(180)]


class DonorLocation(models.Model):
    """
    Where a donor lives.

    PRIVACY: latitude/longitude are the exact point the donor chose and
    must never leave the server. Use approximate_coordinates for anything
    that reaches a template, JSON or the browser.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donor_location",
    )

    province = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICES,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=LATITUDE_VALIDATORS,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=LONGITUDE_VALIDATORS,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.province}"

    @property
    def approximate_coordinates(self):
        """(lat, lng) rounded to about 1 km. Safe to show to users."""
        return approximate(self.latitude, self.longitude)


class Facility(models.Model):

    class FacilityType(models.TextChoices):
        HOSPITAL = "HOSPITAL", "Hospital"
        DONATION_CENTER = "DONATION_CENTER", "Donation Center"

    name = models.CharField(max_length=200)

    facility_type = models.CharField(
        max_length=20,
        choices=FacilityType.choices,
        default=FacilityType.HOSPITAL,
    )

    province = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICES,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    address = models.CharField(
        max_length=255,
        blank=True,
    )

    # Facilities are public places, so exact coordinates are fine here.
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=LATITUDE_VALIDATORS,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=LONGITUDE_VALIDATORS,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "facilities"

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"
