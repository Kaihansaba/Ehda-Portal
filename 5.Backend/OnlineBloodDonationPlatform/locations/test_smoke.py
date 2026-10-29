"""
Smoke and edge-case tests for the whole site.

1. Every named URL in config/urls.py is requested as each role
   (anonymous, donor, hospital, admin). No request may raise or return a
   500, and each must give the expected page, redirect or 403.
2. Every Django admin model page loads for a superuser.
3. Search and map edge cases: missing locations, no donors, invalid or
   extreme query-string values.
"""
from decimal import Decimal

from django.contrib import admin
from django.test import TestCase
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from accounts.models import BloodRequest, User
from locations.models import DonorLocation
from locations.search import search_donors


PASSWORD = "StrongPass123!"

ROLES = ("anonymous", "donor", "hospital", "admin")

# URLs that need arguments: dummy values are fine for a smoke test.
URL_ARGS = {
    "password_reset_confirm": {"uidb64": "MQ", "token": "invalid-token"},
}


def login_url(next_url):
    return f"{reverse('login')}?next={next_url}"


def all_named_urls():
    """namespace:name for every named URL, except the Django admin."""
    names = []

    def walk(patterns, namespace=""):
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                if pattern.namespace == "admin":
                    continue
                child = f"{namespace}{pattern.namespace}:" if pattern.namespace else namespace
                walk(pattern.url_patterns, child)
            elif isinstance(pattern, URLPattern) and pattern.name:
                names.append(namespace + pattern.name)

    walk(get_resolver().url_patterns)
    return names


def expected(name, url):
    """
    What each role should get for a URL: (status, redirect target).
    redirect target is None when no redirect is expected.
    """
    dashboard = {
        "donor": reverse("donor_dashboard"),
        "hospital": reverse("hospital_dashboard"),
        "admin": reverse("admin_dashboard"),
    }

    def public():
        return {role: (200, None) for role in ROLES}

    def logged_in(page_for_users=(200, None)):
        result = {role: page_for_users for role in ROLES}
        result["anonymous"] = (302, login_url(url))
        return result

    def only(*roles):
        result = {role: (403, None) for role in ROLES}
        result["anonymous"] = (302, login_url(url))
        for role in roles:
            result[role] = (200, None)
        return result

    table = {
        "index": {
            "anonymous": (302, reverse("login")),
            "donor": (302, reverse("role_redirect")),
            "hospital": (302, reverse("role_redirect")),
            "admin": (302, reverse("role_redirect")),
        },
        "register": public(),
        "login": public(),
        # GET does not log out; it sends the user to their dashboard.
        "logout": {role: (302, reverse("role_redirect")) for role in ROLES},
        "home": logged_in(),
        "role_redirect": {
            "anonymous": (302, login_url(url)),
            **{role: (302, dashboard[role]) for role in ("donor", "hospital", "admin")},
        },
        "donor_dashboard": only("donor"),
        "donor_profile": only("donor"),
        "donation_history": only("donor"),
        # Donor side of blood requests (#011, #012)
        "donor_blood_requests": only("donor"),
        # GET does not answer; donors go back to their request list.
        "respond_to_request": {
            **only(),
            "donor": (302, reverse("donor_blood_requests")),
        },
        # GET does not toggle; donors are sent back to their dashboard.
        "toggle_availability": {
            **only(),
            "donor": (302, reverse("donor_dashboard")),
        },
        "hospital_dashboard": only("hospital"),
        # Blood requests (Developer 3): hospitals only
        "manage_blood_requests": only("hospital"),
        "create_blood_request": only("hospital"),
        "request_detail": only("hospital"),
        # GET does not change a status; hospitals go back to their list.
        "change_request_status": {
            **only(),
            "hospital": (302, reverse("manage_blood_requests")),
        },
        "close_blood_request": {
            **only(),
            "hospital": (302, reverse("manage_blood_requests")),
        },
        "admin_dashboard": only("admin"),
        # Admin tools (Developer 3): admins only
        "admin_manage_users": only("admin"),
        "admin_manage_hospitals": only("admin"),
        "admin_reported_accounts": only("admin"),
        "admin_platform_activity": only("admin"),
        "admin_platform_statistics": only("admin"),
        "admin_security_access": only("admin"),
        # GET does not toggle; admins go back to Manage users.
        "toggle_user_status": {
            **only(),
            "admin": (302, reverse("admin_manage_users")),
        },
        "password_reset": public(),
        "password_reset_done": public(),
        "password_reset_confirm": public(),
        "password_reset_complete": public(),
        "locations:donor_location": only("donor"),
        "locations:search": only("donor", "hospital", "admin"),
        "locations:map": only("donor", "hospital", "admin"),
    }

    return table.get(name)


class UrlSmokeTests(TestCase):

    def setUp(self):
        self.users = {
            "donor": User.objects.create_user(
                email="donor@example.com", password=PASSWORD,
                first_name="Dina", last_name="Donor", role="DONOR", blood_type="O-",
            ),
            "hospital": User.objects.create_user(
                email="hospital@example.com", password=PASSWORD,
                first_name="City", last_name="Hospital", role="HOSPITAL",
            ),
            "admin": User.objects.create_superuser(
                email="admin@example.com", password=PASSWORD,
                first_name="Ada", last_name="Admin",
            ),
        }
        DonorLocation.objects.create(
            user=self.users["donor"], province="Kabul",
            latitude=Decimal("34.531234"), longitude=Decimal("69.171234"),
        )
        blood_request = BloodRequest.objects.create(
            hospital=self.users["hospital"], blood_type="O-", notes="Surgery",
        )

        # URLs that need real objects: the hospital's own request, a donor.
        self.url_args = {
            **URL_ARGS,
            "request_detail": {"pk": blood_request.pk},
            "change_request_status": {"pk": blood_request.pk, "status": "IN_REVIEW"},
            "close_blood_request": {"pk": blood_request.pk},
            "respond_to_request": {"pk": blood_request.pk},
            "toggle_user_status": {"pk": self.users["donor"].pk},
        }

    def login_as(self, role):
        self.client.logout()
        if role != "anonymous":
            self.client.force_login(self.users[role])

    def test_every_url_has_an_expectation(self):
        missing = [name for name in all_named_urls() if expected(name, "/") is None]

        self.assertEqual(missing, [], "Add these URLs to expected() in test_smoke.py")

    def test_every_url_for_every_role(self):
        for name in all_named_urls():
            url = reverse(name, kwargs=self.url_args.get(name))
            expectations = expected(name, url)

            for role in ROLES:
                with self.subTest(url=url, role=role):
                    self.login_as(role)
                    response = self.client.get(url)
                    status, target = expectations[role]

                    self.assertLess(response.status_code, 500)
                    self.assertEqual(response.status_code, status)
                    if target is not None:
                        self.assertRedirects(response, target, fetch_redirect_response=False)

    def test_admin_requires_staff(self):
        admin_index = reverse("admin:index")

        for role in ("anonymous", "donor", "hospital"):
            with self.subTest(role=role):
                self.login_as(role)
                response = self.client.get(admin_index)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("admin:login"), response["Location"])

    def test_every_admin_model_page_loads_for_superuser(self):
        self.login_as("admin")
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)

        for model in admin.site._registry:
            info = (model._meta.app_label, model._meta.model_name)
            for page in ("changelist", "add"):
                with self.subTest(model=model.__name__, page=page):
                    url = reverse(f"admin:{info[0]}_{info[1]}_{page}")
                    self.assertEqual(self.client.get(url).status_code, 200)


class SearchAndMapEdgeCaseTests(TestCase):

    def setUp(self):
        self.hospital = User.objects.create_user(
            email="hospital@example.com", password=PASSWORD,
            first_name="City", role="HOSPITAL",
        )
        self.client.force_login(self.hospital)
        self.search_url = reverse("locations:search")
        self.map_url = reverse("locations:map")

    def make_donor(self, email, blood_type="A+", latitude="34.54", longitude="69.18", location=True):
        user = User.objects.create_user(
            email=email, password=PASSWORD, first_name="Don", last_name="Or",
            role="DONOR", blood_type=blood_type,
        )
        if location:
            DonorLocation.objects.create(
                user=user, province="Kabul",
                latitude=Decimal(latitude), longitude=Decimal(longitude),
            )
        return user

    def search(self, **params):
        response = self.client.get(self.search_url, params)
        self.assertEqual(response.status_code, 200)
        return response

    def test_no_donors_at_all(self):
        response = self.search(blood_type="A+", latitude="34.53", longitude="69.17", radius="50")

        self.assertEqual(response.context["results"], [])
        self.assertContains(response, "No donors match your search")

        map_response = self.client.get(self.map_url)
        self.assertEqual(map_response.status_code, 200)
        self.assertEqual(map_response.context["map_data"]["donors"], [])

    def test_donor_without_location_is_not_listed(self):
        self.make_donor("noloc@example.com", location=False)

        response = self.search(blood_type="A+")

        self.assertEqual(response.context["results"], [])
        self.assertEqual(self.client.get(self.map_url).context["map_data"]["donors"], [])

    def test_searcher_without_location(self):
        self.make_donor("withloc@example.com")

        # Hospital has no location: map centres on Afghanistan, search works.
        map_response = self.client.get(self.map_url)
        self.assertEqual(map_response.context["map_data"]["center"]["zoom"], 6)

        response = self.search(blood_type="A+")
        self.assertEqual(len(response.context["results"]), 1)

        # A distance with no point or province is a form error, not a crash.
        response = self.search(blood_type="A+", radius="10")
        self.assertTrue(response.context["form"].errors.get("radius"))

    def test_donor_searcher_without_location(self):
        searcher = self.make_donor("searcher@example.com", location=False)
        self.make_donor("other@example.com")
        self.client.force_login(searcher)

        response = self.search(blood_type="A+")
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(self.client.get(self.map_url).status_code, 200)

    def test_invalid_query_values_show_form_errors(self):
        cases = [
            {"blood_type": "ZZ"},
            {"blood_type": "A+", "radius": "abc"},
            {"blood_type": "A+", "radius": "100000"},
            {"blood_type": "A+", "radius": "-5"},
            {"blood_type": "A+", "province": "Atlantis"},
            {"blood_type": "A+", "latitude": "abc", "longitude": "69.17"},
            {"blood_type": "A+", "latitude": "nan", "longitude": "nan"},
            {"blood_type": "A+", "latitude": "999", "longitude": "999"},
            {"blood_type": "A+", "latitude": "34.53"},
            {"blood_type": "A+", "latitude": "51.5", "longitude": "-0.12"},
        ]

        for params in cases:
            with self.subTest(params=params):
                response = self.search(**params)
                self.assertTrue(response.context["form"].errors)
                self.assertIsNone(response.context["results"])

    def test_invalid_map_filter_is_ignored(self):
        self.make_donor("a@example.com", blood_type="A+")

        for value in ("ZZ", "", "A+' OR 1=1", "x" * 500):
            with self.subTest(blood_type=value):
                response = self.client.get(self.map_url, {"blood_type": value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context["map_data"]["donors"]), 1)

    def test_very_large_radius_returns_everyone(self):
        self.make_donor("kabul@example.com")
        self.make_donor("herat@example.com", latitude="34.34", longitude="62.20")

        results = search_donors(
            searcher=self.hospital, blood_type="A+",
            origin=(34.53, 69.17), radius_km=20000,
        )

        self.assertEqual(len(results), 2)
        self.assertLess(results[0].distance_km, results[1].distance_km)

    def test_largest_radius_choice_works(self):
        self.make_donor("kabul@example.com")

        response = self.search(blood_type="A+", latitude="34.53", longitude="69.17", radius="50")

        self.assertEqual(len(response.context["results"]), 1)

    def test_invalid_location_post_values(self):
        donor = self.make_donor("setter@example.com", location=False)
        self.client.force_login(donor)
        url = reverse("locations:donor_location")

        for latitude, longitude in (("abc", "69.17"), ("nan", "nan"), ("999", "999"), ("", "69.17")):
            with self.subTest(latitude=latitude, longitude=longitude):
                response = self.client.post(url, {
                    "province": "Kabul", "latitude": latitude, "longitude": longitude,
                })
                self.assertEqual(response.status_code, 200)
                self.assertFalse(DonorLocation.objects.filter(user=donor).exists())
