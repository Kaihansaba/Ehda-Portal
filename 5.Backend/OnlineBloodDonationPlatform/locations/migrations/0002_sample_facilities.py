from decimal import Decimal

from django.db import migrations


# ---------------------------------------------------------------------
# SAMPLE DATA - FOR DEVELOPMENT AND DEMOS ONLY.
#
# Names, addresses and coordinates below are approximate and have NOT
# been verified. The team must check every entry (and add phone numbers)
# before this data is shown to real users. Facilities can be corrected
# or deactivated in Django admin.
# ---------------------------------------------------------------------
SAMPLE_FACILITIES = [
    # Kabul
    {
        "name": "Wazir Akbar Khan Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Kabul",
        "district": "Kabul City",
        "address": "Wazir Akbar Khan area, Kabul (verify)",
        "latitude": "34.537000",
        "longitude": "69.192000",
    },
    {
        "name": "Jamhuriat Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Kabul",
        "district": "Kabul City",
        "address": "Central Kabul (verify)",
        "latitude": "34.523000",
        "longitude": "69.168000",
    },
    {
        "name": "Indira Gandhi Children's Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Kabul",
        "district": "Kabul City",
        "address": "Kabul (verify)",
        "latitude": "34.528000",
        "longitude": "69.137000",
    },
    {
        "name": "Kabul Central Blood Bank (sample)",
        "facility_type": "DONATION_CENTER",
        "province": "Kabul",
        "district": "Kabul City",
        "address": "Kabul (verify)",
        "latitude": "34.530000",
        "longitude": "69.160000",
    },
    # Herat
    {
        "name": "Herat Regional Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Herat",
        "district": "Herat City",
        "address": "Herat (verify)",
        "latitude": "34.345000",
        "longitude": "62.195000",
    },
    {
        "name": "Herat Blood Bank (sample)",
        "facility_type": "DONATION_CENTER",
        "province": "Herat",
        "district": "Herat City",
        "address": "Herat (verify)",
        "latitude": "34.350000",
        "longitude": "62.205000",
    },
    # Balkh
    {
        "name": "Mazar-i-Sharif Regional Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Balkh",
        "district": "Mazar-i-Sharif",
        "address": "Mazar-i-Sharif (verify)",
        "latitude": "36.705000",
        "longitude": "67.110000",
    },
    # Kandahar
    {
        "name": "Mirwais Regional Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Kandahar",
        "district": "Kandahar City",
        "address": "Kandahar (verify)",
        "latitude": "31.620000",
        "longitude": "65.700000",
    },
    # Nangarhar
    {
        "name": "Nangarhar Regional Hospital (sample)",
        "facility_type": "HOSPITAL",
        "province": "Nangarhar",
        "district": "Jalalabad",
        "address": "Jalalabad (verify)",
        "latitude": "34.430000",
        "longitude": "70.450000",
    },
]


def add_sample_facilities(apps, schema_editor):
    Facility = apps.get_model("locations", "Facility")

    for data in SAMPLE_FACILITIES:
        Facility.objects.get_or_create(
            name=data["name"],
            defaults={
                **data,
                "latitude": Decimal(data["latitude"]),
                "longitude": Decimal(data["longitude"]),
            },
        )


def remove_sample_facilities(apps, schema_editor):
    Facility = apps.get_model("locations", "Facility")

    Facility.objects.filter(
        name__in=[data["name"] for data in SAMPLE_FACILITIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            add_sample_facilities,
            remove_sample_facilities,
        ),
    ]
