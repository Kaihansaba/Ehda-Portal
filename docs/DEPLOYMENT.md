# Deploying Ehda Portal on PythonAnywhere

This guide puts Ehda Portal online on a free PythonAnywhere account, with
HTTPS and the SQLite database. It takes about 20 minutes.

Replace these placeholders everywhere:

| Placeholder | Meaning | Example |
|---|---|---|
| `<username>` | Your PythonAnywhere username. The free site address is `<username>.pythonanywhere.com`. | `ehdaportal` |
| `<repo-url>` | The GitHub address of this repository | `https://github.com/Kaihansaba/Ehda-Portal.git` |

The Django project lives in `5.Backend/OnlineBloodDonationPlatform/` inside
the repository; every command below runs from that folder.

## 1. Create the account and check the Python version

1. Sign up at <https://www.pythonanywhere.com/> (the free “Beginner”
   account is enough). Your username becomes the site address.
2. Ehda needs **Python 3.12 or newer** (Django 6.1). Open the
   **Account** page, **System image** tab, and choose the newest image if
   your account offers an older one. Then open a **Bash console**
   (**Consoles** tab, **Bash**) and check:

   ```bash
   python3.13 --version    # or python3.12 --version
   ```

   Use whichever of `python3.13` / `python3.12` exists in every command
   below. The steps show `python3.13`.

## 2. Get the code

In the Bash console:

```bash
cd ~
git clone <repo-url> Ehda-Portal
cd ~/Ehda-Portal/5.Backend/OnlineBloodDonationPlatform
```

If the repository is private, GitHub asks for a username and a
**personal access token** (not your password): GitHub, Settings,
Developer settings, Personal access tokens.

## 3. Create the virtual environment and install packages

```bash
python3.13 -m venv ~/.virtualenvs/ehda
source ~/.virtualenvs/ehda/bin/activate
pip install -r requirements.txt
```

Your prompt now starts with `(ehda)`. Whenever you open a new console,
run `source ~/.virtualenvs/ehda/bin/activate` again before using
`python manage.py`.

## 4. Create the `.env` file

First make a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Copy the example file and edit it:

```bash
cp .env.example .env
nano .env
```

Set at least these values (keep the rest as they are):

```ini
DJANGO_SECRET_KEY=<paste the key you just generated>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://<username>.pythonanywhere.com
```

Save with **Ctrl+O**, **Enter**, then exit with **Ctrl+X**.

- Leave the `EMAIL_*` login values empty: the free tier blocks SMTP.
  Emails (notifications, password reset) are then written to the
  **Server log** instead of being sent, and never break a page.
- Never commit `.env`; it is already in `.gitignore`.

Every variable is explained in `.env.example`.

## 5. Create the database, static files and accounts

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

- `migrate` creates `db.sqlite3` with every table and the sample
  hospitals and donation centres shown on the map.
- `collectstatic` copies the CSS, JavaScript and icons (and the Django
  admin's) into `staticfiles/`, which PythonAnywhere serves directly.

**Demo accounts (optional, for presenting the project).** On a live site
the published demo password is refused, so choose your own:

```bash
python manage.py create_demo_accounts --password 'Choose-A-Demo-Password-2026'
```

This creates `admin@ehda.test`, `hospital@ehda.test`,
`donor@ehda.test` and five more donors, all with that password. Share it
only with the people who need to try the site.

**Your own administrator account:**

```bash
python manage.py createsuperuser
```

It asks for an email address and a password. Use this account to sign in
to the site and to `/admin/`.

## 6. Create the web app (Web tab)

Open the **Web** tab.

1. Click **Add a new web app**, then **Next**.
2. Choose **Manual configuration** (not “Django”).
3. Choose the **same Python version** as the virtual environment
   (e.g. Python 3.13), then **Next**.

On the web app's page, fill in:

| Section | Field | Value |
|---|---|---|
| Code | Source code | `/home/<username>/Ehda-Portal/5.Backend/OnlineBloodDonationPlatform` |
| Code | Working directory | `/home/<username>/Ehda-Portal/5.Backend/OnlineBloodDonationPlatform` |
| Virtualenv | Path | `/home/<username>/.virtualenvs/ehda` |

## 7. The WSGI file

In the **Code** section, click the **WSGI configuration file** link
(`/var/www/<username>_pythonanywhere_com_wsgi.py`). Delete everything in
it and paste this, with your username in the path:

```python
import os
import sys

# The folder that contains manage.py
path = "/home/<username>/Ehda-Portal/5.Backend/OnlineBloodDonationPlatform"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Click **Save**. The settings read `.env` from the project folder
themselves, so nothing else is needed here.

## 8. Static files mapping

In the **Static files** section, click **Enter URL** / **Enter path** and
add one row:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/Ehda-Portal/5.Backend/OnlineBloodDonationPlatform/staticfiles` |

## 9. Force HTTPS

In the **Security** section, switch **Force HTTPS** on.
PythonAnywhere then redirects every `http://` visit to `https://`.
Django already trusts PythonAnywhere's HTTPS proxy, and with
`DJANGO_DEBUG=False` its login and form cookies are only sent over
HTTPS. (`DJANGO_SECURE_SSL_REDIRECT` stays `False`; the redirect is
PythonAnywhere's job.)

## 10. Reload and test

1. Click the green **Reload** button at the top of the Web tab.
2. Open `https://<username>.pythonanywhere.com/`. You should see the
   sign-in page with the Ehda design.
3. Sign in with your superuser, open the map (tiles should load), and
   open a page that doesn't exist, e.g. `/no-such-page/`. You should see
   Ehda's own “Page not found” page, not a yellow Django error page.

Optional, once HTTPS has worked for a while: set
`DJANGO_SECURE_HSTS_SECONDS=3600` in `.env` (later `31536000`) and
reload. Browsers then refuse plain HTTP for your site. Read the comment
in `.env.example` first.

**Free accounts:** the web app is switched off after three months unless
you click **Run until 3 months from today** on the Web tab.
PythonAnywhere emails a reminder.

## Updating the site later

In a Bash console:

```bash
cd ~/Ehda-Portal
git pull
cd 5.Backend/OnlineBloodDonationPlatform
source ~/.virtualenvs/ehda/bin/activate
pip install -r requirements.txt          # only installs what changed
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** on the Web tab. Changes don't appear until you
reload.

Back up the database before big updates: download `db.sqlite3` from the
**Files** tab, or `cp db.sqlite3 db.sqlite3.backup` in the console.

## When something goes wrong

The Web tab links to an **Error log** and a **Server log**. Errors and
email output are written there. Check the newest lines at the bottom
first.

| What you see | Likely cause | Fix |
|---|---|---|
| “Something went wrong” page, or *ImproperlyConfigured* in the error log | `DJANGO_SECRET_KEY` missing or still a placeholder while `DJANGO_DEBUG=False` | Set a real key in `.env`, then Reload |
| “Bad Request (400)” | The site's address isn't in `DJANGO_ALLOWED_HOSTS` | Add `<username>.pythonanywhere.com`, then Reload |
| “Forbidden (403) CSRF verification failed” when submitting a form | `DJANGO_CSRF_TRUSTED_ORIGINS` missing, or without `https://` | Set it to `https://<username>.pythonanywhere.com`, then Reload |
| Page has no styling | `collectstatic` not run, or the static files row has a typo | Run `collectstatic`, check the `/static/` row, Reload |
| *no such table* in the error log | `migrate` not run after an update | Run `python manage.py migrate`, then Reload |
| *ModuleNotFoundError: No module named 'django'* | The Virtualenv path on the Web tab is wrong or empty | Set it to `/home/<username>/.virtualenvs/ehda`, then Reload |
| Map has no tiles | The browser blocks `tile.openstreetmap.org`, or it is down | Tiles load in the visitor's browser, not on the server; try another network |
| Emails never arrive | Normal on the free tier (SMTP blocked) | Read them in the Server log |
