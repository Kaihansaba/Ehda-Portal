# Database

The database is defined in code with Django models and migrations.
Development uses SQLite (`db.sqlite3`, created by `python manage.py migrate`
and not committed to git).

| What | Where |
|---|---|
| User model (email login, role, blood type, availability) | [`5.Backend/OnlineBloodDonationPlatform/accounts/models.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/models.py) |
| Donor locations and facilities (hospitals, donation centres) | [`5.Backend/OnlineBloodDonationPlatform/locations/models.py`](../5.Backend/OnlineBloodDonationPlatform/locations/models.py) |
| Migrations (schema history) | [`5.Backend/OnlineBloodDonationPlatform/accounts/migrations/`](../5.Backend/OnlineBloodDonationPlatform/accounts/migrations/), [`5.Backend/OnlineBloodDonationPlatform/locations/migrations/`](../5.Backend/OnlineBloodDonationPlatform/locations/migrations/) |
| Sample facilities (data migration) | [`5.Backend/OnlineBloodDonationPlatform/locations/migrations/0002_sample_facilities.py`](../5.Backend/OnlineBloodDonationPlatform/locations/migrations/0002_sample_facilities.py) |
| Database settings | [`5.Backend/OnlineBloodDonationPlatform/config/settings.py`](../5.Backend/OnlineBloodDonationPlatform/config/settings.py) |

Privacy: `DonorLocation` stores the exact point a donor chose, but only
coordinates rounded to about 1 km are ever shown to other users.
