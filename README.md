# Ehda Portal

**Ehda** (اهدا, “donation” in Dari) is an online blood donation platform
for Afghanistan. It connects people who need blood with willing donors and
with hospitals and donation centres.

- **Donors** register, set their blood type, availability and an
  approximate location, answer blood requests that match their blood
  type, message the hospital after accepting, and keep a record of their
  donations.
- **Hospitals** search for donors by blood type (including compatible
  types) and distance, send a request to all compatible donors or to one
  chosen donor, see who accepted, and message or call them.
- **Administrators** manage users, hospitals and donation centres, review
  reported accounts, and monitor requests and platform activity.
- **Everyone** gets in-app notifications (also by email), can report an
  account they dealt with, and can change their password.
- **Privacy:** donors' exact locations are never shown (rounded to about
  1 km), and their email address is never shown to other users. A donor's
  full name and phone number go only to the hospital whose request they
  accepted, and donors can keep their phone number and area private.

Software Engineering project, American University of Afghanistan (AUAF),
built in four Scrum sprints.

## Team

| Name | Role | Responsibilities |
|---|---|---|
| Madina Pasun | Product Owner | Product backlog, requirements (SRS, user stories, acceptance criteria), sprint planning and review documents |
| Madina Afshar | Scrum Master | Daily Scrum, sprint coordination, burndown charts, removing blockers |
| Samira Azizi | Developer 1 | Registration, login, donor profile, availability, donation history |
| Ahmad Kaihan Saba | Developer 2 | Donor search, interactive map, location privacy, shared UI design |
| Shafiqa Taraki | Developer 3 | Blood requests and status rules, admin tools |

Details: [Roles and Responsibilities](0.Project-documents/Roles-and-Responsibilities.md).

## Features by user story

Checked against the acceptance criteria in
[0.Project-documents/Acceptance-Criteria.md](0.Project-documents/Acceptance-Criteria.md).
“Partial” means the feature works but some criteria are not met yet; the
last column says which.

| Story | Feature | Status | Not done yet |
|---|---|---|---|
| #001 | Registration | Done | |
| #002 | Login, logout, password reset | Done | |
| #003 | Donor profile | Done | Includes privacy settings: share phone after accepting, show area on search and map |
| #004 | Blood type and donation information | Done | Blood type is self-reported, not medically verified |
| #005 | Availability status | Done | |
| #006 | Search by blood type (with ABO/Rh compatibility) | Done | |
| #007 | Search by location and distance, nearest first | Done | |
| #008 | Map of donors, hospitals and donation centres | Done | |
| #009 | Location privacy (approximate locations only) | Done | |
| #010 | Blood requests | Done | To all compatible donors, or to one donor chosen in search |
| #011 | Request notifications | Done | In-app notifications plus email; no mobile push |
| #012 | Accept or decline a request | Partial | A donor's answer doesn't change the request status (the hospital updates it) |
| #013 | Request responses for the seeker | Done | Hospitals act as the blood seeker; they see each donor's answer and a badge for new acceptances |
| #014 | Messaging after acceptance | Done | Refreshes every 10 seconds (not instant); messages are protected by HTTPS in transit once deployed, not encrypted in the database |
| #015 | Donation history | Done | |
| #016 | Account management | Done | Donors: profile page; hospitals and admins: account page; password change for everyone |
| #017 | User management (admin) | Done | Search is in the site admin (`/admin/`) |
| #018 | Hospitals and donation centres (admin) | Done | Managed in the site admin; shown on the map |
| #019 | Reported accounts | Done | Only people who dealt with each other (a request or messages) can report each other |
| #020 | Platform monitoring | Done | |

Not built: a separate “blood seeker” account type (hospitals play that
role), and mobile push notifications. A donor's answer is recorded but
doesn't change the request status by itself (#012); the hospital moves
the request through its statuses.

## Tech stack

- Python 3.12+ and [Django 6.1](https://docs.djangoproject.com/en/6.1/)
- SQLite for development
- Server-rendered Django templates, one hand-written stylesheet and a
  little vanilla JavaScript (no framework, no build step); see
  [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md)
- [Leaflet](https://leafletjs.com/) and OpenStreetMap tiles for maps (free, no API key)

## Setup and run

You need Python 3.12 or newer. All commands run from the Django project
folder, `5.Backend/OnlineBloodDonationPlatform`.

### macOS / Linux

```bash
cd 5.Backend/OnlineBloodDonationPlatform

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py create_demo_accounts   # optional, see below
python manage.py runserver
```

### Windows (PowerShell)

```powershell
cd 5.Backend\OnlineBloodDonationPlatform

py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py create_demo_accounts   # optional, see below
python manage.py runserver
```

**If PowerShell says “running scripts is disabled on this system”** when
you activate, allow local scripts for your user once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

Or use Command Prompt instead: `.venv\Scripts\activate.bat`.

Then open <http://127.0.0.1:8000/>.

After pulling new code, run `python manage.py migrate` again: new
features can add database tables.

### Settings

The app runs with no configuration. To change settings, copy
`.env.example` to `.env` in the same folder and edit it. `.env` is
git-ignored; never commit it.

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | development key | Required (a long random value) when `DJANGO_DEBUG` is `False`; placeholders are refused |
| `DJANGO_DEBUG` | `True` | Use `False` in production |
| `DJANGO_ALLOWED_HOSTS` | empty | Comma-separated host names, needed when `DEBUG` is off |
| `EMAIL_*` | console | Password-reset emails print in the terminal. Set the `EMAIL_*` values (see `.env.example`) to send real email, e.g. with a Gmail app password |

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

From `5.Backend/OnlineBloodDonationPlatform`, with the virtual
environment active:

```bash
python manage.py test                    # everything (about 290 tests)
python manage.py test accounts           # one app
python manage.py test locations.test_smoke
```

The tests cover registration and permissions, search and distance, the
map, location privacy and privacy settings, blood requests (including
targeted ones) and their status rules, donor answers and contact
sharing, notifications and email, messaging, reports, donation records,
accounts and password change, admin tools, error pages, and a smoke test
that opens every page as every role. See
[7.Tests/README.md](7.Tests/README.md).

## Folder structure

```
Ehda-Portal/
├── 0.Project-documents/        Project description, SRS, user stories, acceptance criteria,
│                               roles, Sprint 3–4 requirements and traceability matrix (PDF)
├── 1.Project-Backlogs/         Product backlog and sprint backlogs (Sprints 1–4)
├── 2.Meeting-Recordings/       Links to meeting recordings
├── 3.Meeting-Agendas/          Kickoff, sprint planning and review agendas
├── 4.Frontend/                 README only: points to the Django templates and static files
├── 5.Backend/
│   └── OnlineBloodDonationPlatform/    The Django project (all code)
│       ├── manage.py
│       ├── requirements.txt
│       ├── .env.example                Optional settings (copy to .env)
│       ├── config/                     Settings and URL routes
│       ├── accounts/                   Users, dashboards, profiles, blood requests,
│       │                               donor answers, admin tools
│       ├── locations/                  Donor locations, facilities, search, map
│       ├── static/                     ehda.css, ehda-admin.css, ehda.js, maps.js, favicon
│       └── templates/                  All page templates
│           ├── base.html               Layout every page extends
│           ├── 404.html, 500.html      Error pages
│           ├── partials/               Navbar, footer, form field, badges, icons...
│           ├── accounts/
│           ├── locations/
│           └── admin/                  Ehda branding for /admin/
├── 6.Database/                 README only: points to models and migrations
├── 7.Tests/                    README only: points to the test files
├── 8.Scrum Master Documents/   Burndown chart and daily scrum notes
├── 9.Diagrams/                 UML diagrams
│   ├── Sequence-Diagrams/      One per sprint, named “Sprint-N - Topic (Author)”
│   └── Use-Case-Diagrams/
└── docs/
    └── UI_GUIDELINES.md        How to build pages that match the design
```

## Design

Read [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md) before adding or
changing pages: design tokens, components and partials, forms, maps,
privacy rules, accessibility checklist and right-to-left support.

## Before real use

- **Facility data:** the hospitals and donation centres added by the
  `0002_sample_facilities` migration are samples. Their names, addresses
  and coordinates must be checked before real use (editable in `/admin/`).
- **Deployment:** `python manage.py check --deploy` lists the HTTPS
  settings to turn on (HSTS, secure cookies, SSL redirect) once the site
  runs behind HTTPS.
