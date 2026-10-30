from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from locations.models import DonorLocation


DEFAULT_PASSWORD = "EhdaDemo2026!"

# (email, first name, last name, blood type, available, province, district, lat, lng)
# Locations are made-up points for demos only.
DEMO_DONORS = [
    ("donor@ehda.test", "Maryam", "Ahmadi", "O-", True, "Kabul", "District 4", "34.5312", "69.1712"),
    ("farid@ehda.test", "Farid", "Rahimi", "A+", True, "Kabul", "District 10", "34.5510", "69.1820"),
    ("zahra@ehda.test", "Zahra", "Hakimi", "O+", True, "Kabul", "District 3", "34.5120", "69.1430"),
    ("omid@ehda.test", "Omid", "Sadat", "A-", True, "Kabul", "District 11", "34.5810", "69.2110"),
    ("laila@ehda.test", "Laila", "Noori", "B+", False, "Kabul", "District 5", "34.5400", "69.1300"),
    ("jawad@ehda.test", "Jawad", "Amiri", "AB+", True, "Herat", "Herat City", "34.3500", "62.2000"),
]


class Command(BaseCommand):
    help = (
        "Create demo accounts (admin, hospital and several donors with "
        "locations) for development and demos. Safe to run more than once. "
        "With DEBUG off, --password is required."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help=f"Password for every demo account (default: {DEFAULT_PASSWORD})",
        )

    def handle(self, *args, password, **options):
        # The default password is published in the README. On a live site
        # (DEBUG off) anyone could sign in as the demo admin with it.
        if not settings.DEBUG and password == DEFAULT_PASSWORD:
            raise CommandError(
                "DEBUG is off: choose your own demo password, e.g. "
                "python manage.py create_demo_accounts --password 'Your-Own-Password-2026'"
            )
        if len(password) < 10:
            raise CommandError("Use a demo password of at least 10 characters.")

        self.save_user(
            "admin@ehda.test", password,
            first_name="Demo", last_name="Admin", role=User.Role.ADMIN,
            is_staff=True, is_superuser=True,
        )
        self.save_user(
            "hospital@ehda.test", password,
            first_name="Demo Hospital", last_name="", role=User.Role.HOSPITAL,
        )

        for email, first, last, blood, available, province, district, lat, lng in DEMO_DONORS:
            donor = self.save_user(
                email, password,
                first_name=first, last_name=last, role=User.Role.DONOR,
                blood_type=blood, is_available=available,
            )
            DonorLocation.objects.update_or_create(
                user=donor,
                defaults={
                    "province": province,
                    "district": district,
                    "latitude": Decimal(lat),
                    "longitude": Decimal(lng),
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo accounts are ready:"))
        self.stdout.write("  admin@ehda.test     administrator (also Django admin)")
        self.stdout.write("  hospital@ehda.test  hospital")
        self.stdout.write("  donor@ehda.test     donor, O-, Kabul (plus 5 more donors)")
        self.stdout.write(f"  Password for all:   {password}")

    def save_user(self, email, password, **fields):
        fields.setdefault("phone", "0700000000")
        user, _ = User.objects.update_or_create(email=email, defaults=fields)
        user.set_password(password)
        user.save()
        return user
