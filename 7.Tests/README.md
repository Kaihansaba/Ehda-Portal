# Tests

Automated tests live next to the code they test, inside the Django
project, so Django's test runner can find them.

| Tests | Where |
|---|---|
| Registration, login, profile, availability, role permissions | [`test_sprint1.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_sprint1.py) |
| Search, distance, map, location privacy, access control | [`tests.py`](../5.Backend/OnlineBloodDonationPlatform/locations/tests.py) |
| Blood request validation | [`test_blood_requests.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_blood_requests.py) |
| Blood request status rules and the request detail page | [`test_request_status.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_request_status.py) |
| Donor answers (accept/decline), matching by blood type, new-request count | [`test_donor_requests.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_donor_requests.py) |
| Contact sharing after a donor accepts, hospital badge | [`test_contact_after_accept.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_contact_after_accept.py) |
| Hospital dashboard numbers | [`test_hospital_dashboard.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_hospital_dashboard.py) |
| Admin dashboard and donation records | [`test_admin_dashboard.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_admin_dashboard.py) |
| Admin tools: users, hospitals, reported accounts, activity | [`test_admin_tools.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_admin_tools.py) |
| Error pages, feedback messages, secret-key check | [`test_final_fixes.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_final_fixes.py) |
| Sending a request to one chosen donor (#010) | [`test_targeted_requests.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_targeted_requests.py) |
| Notifications and email (#011) | [`test_notifications.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_notifications.py) |
| Messaging after acceptance (#014) | [`test_messaging.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_messaging.py) |
| Reports and admin review (#019) | [`test_reports.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_reports.py) |
| Donors' own donation records (#015) | [`test_donations.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_donations.py) |
| Account page and password change (#016) | [`test_account.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_account.py) |
| Donor privacy settings (#003) | [`test_privacy_settings.py`](../5.Backend/OnlineBloodDonationPlatform/accounts/test_privacy_settings.py) |
| Every URL for every role, search/map edge cases | [`test_smoke.py`](../5.Backend/OnlineBloodDonationPlatform/locations/test_smoke.py) |

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
