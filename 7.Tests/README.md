# Tests

Automated tests live next to the code they test, inside the Django
project, so Django's test runner can find them.

| Tests | Where |
|---|---|
| Registration, login, profile, availability, role permissions | [`5.Backend/OnlineBloodDonationPlatform/accounts/test_sprint1.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_sprint1.py) |
| Search, distance, map, location privacy, access control | [`5.Backend/OnlineBloodDonationPlatform/locations/tests.py`](../5.Backend/OnlineBloodDonationPlatform/locations/tests.py) |
| Every URL for every role, search/map edge cases | [`5.Backend/OnlineBloodDonationPlatform/locations/test_smoke.py`](../5.Backend/OnlineBloodDonationPlatform/locations/test_smoke.py) |

Run them all from `5.Backend/OnlineBloodDonationPlatform/`:

```bash
python manage.py test
```

Run one app or one file:

```bash
python manage.py test locations
python manage.py test locations.test_smoke
```

Use this folder for test plans, manual test cases and test reports.
