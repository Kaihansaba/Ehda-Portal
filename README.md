# SE-project-AUAF-

Ehda Portal: an online blood donation platform (Django + SQLite).

All application code lives in `5.Backend/OnlineBloodDonationPlatform/`.

## Setup

Requires Python 3.12 or newer (Django 6.1).

```bash
cd 5.Backend/OnlineBloodDonationPlatform

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database tables
python manage.py migrate

# 4. Create an admin account (log in at /admin/ or /login/)
python manage.py createsuperuser

# 5. Start the development server, then open http://127.0.0.1:8000/
python manage.py runserver
```

## Running tests

```bash
cd 5.Backend/OnlineBloodDonationPlatform
source .venv/bin/activate
python manage.py test
```

Password-reset emails are printed in the terminal running the server (console email backend).
