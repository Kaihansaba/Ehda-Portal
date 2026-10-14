# Ehda Portal

**Ehda** (اهدا, “donation” in Dari) is an online blood donation platform
for Afghanistan. It connects people who need blood with willing donors and
with hospitals and donation centres.

- Donors create a profile with their blood type, availability and an
  approximate location.
- People who need blood search for donors by blood type (optionally
  including compatible types) and distance, or browse a map.
- Donors’ exact locations, email addresses and phone numbers are never
  shown to other users; locations are rounded to about 1 km.

Software Engineering project, American University of Afghanistan (AUAF).

## Team

The team works in Scrum sprints. See
[`0.Project-documents/Roles and Responsibilities.docx`](0.Project-documents/) for details.

| Name | Role | Responsibilities |
|---|---|---|
| Madina Pasun | Product Owner | Product backlog, requirements, sprint planning and review |
| Madina Afshar | Scrum Master | Daily Scrum, sprint coordination, removing blockers |
| Samira Azizi | Developer 1 | Authentication, user management, donor profiles, donation history |
| Ahmad Kaihan Saba | Developer 2 | Donor search, interactive map, location features |
| Shafiqa Taraki | Developer 3 | Blood requests, notifications, messaging, admin dashboard |

## Features

| Story | Feature | Status |
|---|---|---|
| #001–#002 | Registration, login, logout, password reset | Done |
| #003–#005 | Donor profile, blood type, availability | Done |
| #006 | Search donors by blood type (with ABO/Rh compatibility) | Done |
| #007 | Search by location and distance, nearest first | Done |
| #008 | Map of donors, hospitals and donation centres | Done |
| #009 | Location privacy (approximate locations only) | Done |
| #010–#014 | Blood requests, notifications, responses, messaging | Planned |
| #015–#020 | Donation history, account and admin management | Planned |

## Tech stack

- Python 3.12+ and [Django 6.1](https://docs.djangoproject.com/en/6.1/)
- SQLite for development
- Server-rendered Django templates, one hand-written stylesheet and a
  little vanilla JavaScript (no framework, no build step); see
  [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md)
- [Leaflet](https://leafletjs.com/) and OpenStreetMap tiles for maps (free, no API key)

## Folder structure

```
Ehda-Portal/
├── 0.Project-documents/        Project description, user stories, acceptance criteria, roles
├── 1.Project-Backlogs/         Product and sprint backlogs
├── 2.Meeting-Recordings/
├── 3.Meeting-Agendas/
├── 4.Frontend/                 README only: points to the Django templates
├── 5.Backend/
│   └── OnlineBloodDonationPlatform/    The Django project (all code)
│       ├── manage.py
│       ├── requirements.txt
│       ├── .env.example                Optional settings (copy to .env)
│       ├── config/                     Settings and URL routes
│       ├── accounts/                   Users, login, dashboards, donor profile
│       ├── locations/                  Donor locations, facilities, search, map
│       ├── static/                     ehda.css, ehda-admin.css, ehda.js, maps.js, favicon
│       └── templates/                  All page templates
│           ├── base.html               Layout every page extends
│           ├── partials/               Navbar, footer, form field, donor card, icons...
│           ├── accounts/
│           ├── locations/
│           └── admin/                  Ehda branding for /admin/
├── 6.Database/                 README only: points to models and migrations
├── 7.Tests/                    README only: points to the test files
└── docs/
    └── UI_GUIDELINES.md        How to build pages that match the design
```

## Setup and run

You need Python 3.12 or newer. All commands run from the Django project folder.

### macOS / Linux

```bash
cd 5.Backend/OnlineBloodDonationPlatform

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

### Windows (PowerShell)

```powershell
cd 5.Backend\OnlineBloodDonationPlatform

py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

If PowerShell blocks the activate script, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use
Command Prompt with `.venv\Scripts\activate.bat`.

Then open <http://127.0.0.1:8000/>.

### Settings

The app runs with no configuration. To change settings, copy
`.env.example` to `.env` in the same folder and edit it:

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | development key | Required when `DJANGO_DEBUG` is `False` |
| `DJANGO_DEBUG` | `True` | Use `False` in production |
| `DJANGO_ALLOWED_HOSTS` | empty | Comma-separated host names, needed when `DEBUG` is off |

Password-reset emails are printed in the terminal running the server.

## Demo accounts

After `migrate`, create ready-made accounts for every role:

```bash
python manage.py create_demo_accounts
```

| Email | Role |
|---|---|
| `admin@ehda.test` | Administrator (also signs in to `/admin/`) |
| `hospital@ehda.test` | Hospital |
| `donor@ehda.test` | Donor (O−, Kabul), plus five more donors with locations |

The password for all of them is `EhdaDemo2026!` (change it with
`--password`). The command only runs while `DEBUG` is on and is safe to
run more than once. To create your own administrator instead, run
`python manage.py createsuperuser`.

## Running tests

```bash
python manage.py test                    # everything
python manage.py test accounts           # one app
python manage.py test locations.test_smoke
```

The tests cover accounts and permissions, search and distance, map data,
location privacy, and a smoke test that opens every page as every role.
See [`7.Tests/README.md`](7.Tests/README.md).

## Design

Read [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md) before adding or
changing pages: design tokens, components and partials, forms, maps,
privacy rules, accessibility checklist and right-to-left support.

## Open decisions

- **Who can search for donors:** the “blood seeker” role is not decided
  yet. The allowed roles are set in one place: `DONOR_SEARCH_ROLES` in
  `locations/constants.py`.
- **Facility data:** the hospitals and donation centres added by the
  `0002_sample_facilities` migration are samples. Their names, addresses
  and coordinates must be verified before real use (editable in `/admin/`).
