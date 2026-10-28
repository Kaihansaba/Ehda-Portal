import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from locations.constants import DONOR_SEARCH_ROLES
from locations.models import DonorLocation, Facility
from locations.search import search_donors
from locations.utils import (
    approximate,
    bounding_box,
    compatible_donor_types,
    describe_distance,
    haversine_km,
    public_name,
)


# Search origin used in most tests: central Kabul.
KABUL = (34.53, 69.17)


def make_user(email, role="DONOR", blood_type="A+", **extra):
    fields = {
        "password": "StrongPass123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "0700000000",
        "role": role,
        "blood_type": blood_type,
    }
    fields.update(extra)
    return User.objects.create_user(email=email, **fields)


def make_donor(email, blood_type, latitude, longitude, province="Kabul", **extra):
    user = make_user(email, blood_type=blood_type, **extra)

    DonorLocation.objects.create(
        user=user,
        province=province,
        district="District 1",
        latitude=Decimal(latitude),
        longitude=Decimal(longitude),
    )

    return user


def names(results):
    return [result.name for result in results]


# 1. Utility functions

class UtilsTests(TestCase):

    def test_haversine_one_degree_of_latitude(self):
        # One degree along a meridian is about 111.2 km.
        self.assertAlmostEqual(haversine_km(0, 0, 1, 0), 111.19, delta=0.1)

    def test_haversine_known_city_distance(self):
        # London to Paris is about 343.5 km.
        distance = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertAlmostEqual(distance, 343.5, delta=1)

    def test_haversine_same_point_is_zero(self):
        self.assertAlmostEqual(haversine_km(*KABUL, *KABUL), 0)

    def test_bounding_box_contains_points_at_radius(self):
        min_lat, max_lat, min_lng, max_lng = bounding_box(*KABUL, 10)

        # Points 10 km north and east of the origin are inside the box.
        self.assertLessEqual(haversine_km(*KABUL, max_lat, KABUL[1]), 10.01)
        self.assertLessEqual(haversine_km(*KABUL, KABUL[0], max_lng), 10.01)
        self.assertLess(min_lat, KABUL[0])
        self.assertLess(min_lng, KABUL[1])

    def test_approximate_rounds_to_two_decimals(self):
        self.assertEqual(
            approximate(Decimal("34.541234"), Decimal("69.181234")),
            (34.54, 69.18),
        )

    def test_compatibility_table(self):
        self.assertIn("O-", compatible_donor_types("A+"))
        self.assertNotIn("B+", compatible_donor_types("A+"))
        self.assertEqual(compatible_donor_types("O-"), ["O-"])
        self.assertEqual(len(compatible_donor_types("AB+")), 8)

    def test_describe_distance(self):
        self.assertEqual(describe_distance(0.4), "less than 1 km")
        self.assertEqual(describe_distance(4.3), "about 4 km")

    def test_public_name_is_first_name_and_initial(self):
        user = User(first_name="Ahmad", last_name="saba")
        self.assertEqual(public_name(user), "Ahmad S.")


# 2. Search logic

class DonorSearchTests(TestCase):

    def setUp(self):
        self.searcher = make_user("searcher@example.com", role="HOSPITAL")

        # About 1.4 km from KABUL (approximate point 34.54, 69.18).
        self.near = make_donor(
            "near@example.com", "A+", "34.541234", "69.181234",
            first_name="Near",
        )
        # About 8 km from KABUL (approximate point 34.60, 69.20).
        self.mid = make_donor(
            "mid@example.com", "O-", "34.601234", "69.201234",
            first_name="Mid",
        )
        # Herat, about 640 km away.
        self.far = make_donor(
            "far@example.com", "A+", "34.341234", "62.201234",
            province="Herat", first_name="Far",
        )

    def search(self, **kwargs):
        kwargs.setdefault("searcher", self.searcher)
        return search_donors(**kwargs)

    def test_exact_blood_type_only(self):
        results = self.search(blood_type="A+")

        self.assertCountEqual(names(results), ["Near U.", "Far U."])

    def test_compatible_mode_includes_o_negative_for_a_positive(self):
        results = self.search(blood_type="A+", include_compatible=True)

        self.assertCountEqual(names(results), ["Near U.", "Mid U.", "Far U."])

    def test_compatible_mode_excludes_incompatible_types(self):
        make_donor("bplus@example.com", "B+", "34.55", "69.19", first_name="Bee")

        results = self.search(blood_type="A+", include_compatible=True)

        self.assertNotIn("Bee U.", names(results))

    def test_results_are_ordered_by_distance(self):
        results = self.search(
            blood_type="A+", include_compatible=True, origin=KABUL,
        )

        self.assertEqual(names(results), ["Near U.", "Mid U.", "Far U."])
        self.assertLess(results[0].distance_km, results[1].distance_km)
        self.assertLess(results[1].distance_km, results[2].distance_km)

    def test_radius_filters_far_donors(self):
        within_5 = self.search(
            blood_type="A+", include_compatible=True, origin=KABUL, radius_km=5,
        )
        within_10 = self.search(
            blood_type="A+", include_compatible=True, origin=KABUL, radius_km=10,
        )

        self.assertEqual(names(within_5), ["Near U."])
        self.assertEqual(names(within_10), ["Near U.", "Mid U."])

    def test_province_filter(self):
        results = self.search(blood_type="A+", province="Herat")

        self.assertEqual(names(results), ["Far U."])

    def test_unavailable_donors_are_excluded(self):
        self.near.is_available = False
        self.near.save()

        self.assertNotIn("Near U.", names(self.search(blood_type="A+")))

    def test_inactive_donors_are_excluded(self):
        self.near.is_active = False
        self.near.save()

        self.assertNotIn("Near U.", names(self.search(blood_type="A+")))

    def test_donors_without_location_are_excluded(self):
        make_user("noloc@example.com", blood_type="A+", first_name="Nolo")

        self.assertNotIn("Nolo U.", names(self.search(blood_type="A+")))

    def test_non_donor_roles_are_excluded(self):
        hospital = make_user("hosp2@example.com", role="HOSPITAL", first_name="Hosp")
        DonorLocation.objects.create(
            user=hospital, province="Kabul",
            latitude=Decimal("34.53"), longitude=Decimal("69.17"),
        )

        self.assertNotIn("Hosp U.", names(self.search(blood_type="A+")))

    def test_searcher_is_excluded(self):
        results = self.search(searcher=self.near, blood_type="A+")

        self.assertNotIn("Near U.", names(results))
        self.assertIn("Far U.", names(results))


# 3. Search page

class SearchViewTests(TestCase):

    def setUp(self):
        self.searcher = make_user("searcher@example.com", role="HOSPITAL")
        self.donor = make_donor(
            "private.donor@example.com", "A+", "34.541234", "69.181234",
            first_name="Private", last_name="Surname", phone="0799123456",
        )
        self.client.force_login(self.searcher)

    def test_search_page_without_query_shows_no_results(self):
        response = self.client.get(reverse("locations:search"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["results"])

    def test_search_finds_donor_with_distance(self):
        response = self.client.get(
            reverse("locations:search"),
            {"blood_type": "A+", "latitude": "34.53", "longitude": "69.17", "radius": "5"},
        )

        self.assertContains(response, "Private S.")
        self.assertContains(response, "about 1 km")

    def test_empty_results_message(self):
        response = self.client.get(reverse("locations:search"), {"blood_type": "AB-"})

        self.assertContains(response, "No donors match your search")

    def test_blood_type_is_required(self):
        response = self.client.get(reverse("locations:search"), {"province": "Kabul"})

        self.assertTrue(response.context["form"].errors.get("blood_type"))
        self.assertIsNone(response.context["results"])

    def test_radius_needs_a_location(self):
        response = self.client.get(
            reverse("locations:search"), {"blood_type": "A+", "radius": "10"},
        )

        self.assertTrue(response.context["form"].errors.get("radius"))

    def test_send_request_button_is_disabled_until_requests_exist(self):
        response = self.client.get(reverse("locations:search"), {"blood_type": "A+"})

        self.assertContains(response, "Send request")
        self.assertContains(response, "disabled")

    def test_search_page_does_not_leak_private_donor_data(self):
        response = self.client.get(
            reverse("locations:search"),
            {"blood_type": "A+", "latitude": "34.53", "longitude": "69.17"},
        )
        html = response.content.decode()

        self.assertIn("Private S.", html)
        self.assertNotIn("34.541234", html)
        self.assertNotIn("34.5412", html)
        self.assertNotIn("69.1812", html)
        self.assertNotIn("private.donor@example.com", html)
        self.assertNotIn("0799123456", html)
        self.assertNotIn("Surname", html)


# 4. Map page

class MapViewTests(TestCase):

    def setUp(self):
        self.viewer = make_user("viewer@example.com", role="HOSPITAL")
        self.donor = make_donor(
            "private.donor@example.com", "O-", "34.541234", "69.181234",
            first_name="Private", last_name="Surname", phone="0799123456",
        )
        make_donor("bplus@example.com", "B+", "34.601234", "69.201234", first_name="Bee")
        self.client.force_login(self.viewer)

    def map_data(self, **params):
        response = self.client.get(reverse("locations:map"), params)
        return response, response.context["map_data"]

    def test_map_contains_approximate_donor_and_facilities(self):
        _, data = self.map_data()

        donor = next(d for d in data["donors"] if d["name"] == "Private S.")
        self.assertEqual((donor["lat"], donor["lng"]), (34.54, 69.18))
        self.assertEqual(
            len(data["facilities"]),
            Facility.objects.filter(is_active=True).count(),
        )

    def test_inactive_facilities_are_hidden(self):
        Facility.objects.update(is_active=False)

        _, data = self.map_data()

        self.assertEqual(data["facilities"], [])

    def test_blood_type_filter(self):
        _, data = self.map_data(blood_type="B+")

        self.assertEqual([d["name"] for d in data["donors"]], ["Bee U."])

    def test_viewer_is_not_shown_as_donor(self):
        self.client.force_login(self.donor)

        _, data = self.map_data()

        self.assertNotIn("Private S.", [d["name"] for d in data["donors"]])

    def test_map_page_does_not_leak_private_donor_data(self):
        response, data = self.map_data()
        html = response.content.decode()

        self.assertNotIn("34.5412", html)
        self.assertNotIn("69.1812", html)
        self.assertNotIn("private.donor@example.com", html)
        self.assertNotIn("0799123456", html)
        self.assertNotIn("Surname", html)

        # The JSON handed to the browser only has these donor fields.
        payload = json.loads(json.dumps(data))
        for donor in payload["donors"]:
            self.assertEqual(set(donor), {"name", "blood_type", "lat", "lng"})

    def test_donor_names_are_escaped_in_json(self):
        make_donor("xss@example.com", "A+", "34.55", "69.19", first_name="</script><b>x")

        response = self.client.get(reverse("locations:map"))

        self.assertNotIn("</script><b>", response.content.decode())


# 5. Donor location page

class DonorLocationViewTests(TestCase):

    def setUp(self):
        self.donor = make_user("donor@example.com")
        self.client.force_login(self.donor)
        self.url = reverse("locations:donor_location")

    def test_donor_can_set_location(self):
        response = self.client.post(self.url, {
            "province": "Kabul",
            "district": "District 10",
            "latitude": "34.541234",
            "longitude": "69.181234",
        })

        self.assertRedirects(response, self.url)
        location = DonorLocation.objects.get(user=self.donor)
        self.assertEqual(location.latitude, Decimal("34.541234"))
        self.assertEqual(location.district, "District 10")

    def test_location_requires_a_map_click(self):
        response = self.client.post(self.url, {"province": "Kabul"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertFalse(DonorLocation.objects.filter(user=self.donor).exists())

    def test_location_outside_afghanistan_is_rejected(self):
        response = self.client.post(self.url, {
            "province": "Kabul", "latitude": "51.5", "longitude": "-0.12",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(DonorLocation.objects.filter(user=self.donor).exists())

    def test_changing_district_keeps_existing_point(self):
        DonorLocation.objects.create(
            user=self.donor, province="Kabul",
            latitude=Decimal("34.541234"), longitude=Decimal("69.181234"),
        )

        self.client.post(self.url, {"province": "Kabul", "district": "District 5"})

        location = DonorLocation.objects.get(user=self.donor)
        self.assertEqual(location.district, "District 5")
        self.assertEqual(location.latitude, Decimal("34.541234"))

    def test_location_page_never_shows_stored_exact_point(self):
        DonorLocation.objects.create(
            user=self.donor, province="Kabul",
            latitude=Decimal("34.541234"), longitude=Decimal("69.181234"),
        )

        html = self.client.get(self.url).content.decode()

        self.assertNotIn("34.5412", html)
        self.assertNotIn("69.1812", html)

    def test_donor_dashboard_links_to_location_page(self):
        response = self.client.get(reverse("donor_dashboard"))

        self.assertContains(response, self.url)


# 6. Access control

class AccessControlTests(TestCase):

    def test_anonymous_users_are_redirected_to_login(self):
        for name in ["locations:search", "locations:map", "locations:donor_location"]:
            url = reverse(name)
            response = self.client.get(url)

            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_only_donors_can_edit_location(self):
        for role in ["HOSPITAL", "ADMIN"]:
            user = make_user(f"{role.lower()}@example.com", role=role)
            self.client.force_login(user)

            get_response = self.client.get(reverse("locations:donor_location"))
            post_response = self.client.post(reverse("locations:donor_location"), {
                "province": "Kabul", "latitude": "34.53", "longitude": "69.17",
            })

            self.assertEqual(get_response.status_code, 403)
            self.assertEqual(post_response.status_code, 403)

        self.assertFalse(DonorLocation.objects.exists())

    def test_search_roles_can_open_search_and_map(self):
        for role in DONOR_SEARCH_ROLES:
            user = make_user(f"{role.lower()}-search@example.com", role=role)
            self.client.force_login(user)

            self.assertEqual(self.client.get(reverse("locations:search")).status_code, 200)
            self.assertEqual(self.client.get(reverse("locations:map")).status_code, 200)


# 7. Sprint 2 fixes to existing pages

class SetupFixTests(TestCase):

    def setUp(self):
        self.donor = make_user("donor@example.com")

    def test_root_redirects_anonymous_users_to_login(self):
        self.assertRedirects(self.client.get("/"), reverse("login"))

    def test_root_redirects_logged_in_users_to_dashboard(self):
        self.client.force_login(self.donor)

        response = self.client.get("/", follow=True)

        self.assertEqual(response.request["PATH_INFO"], reverse("donor_dashboard"))

    def test_login_follows_safe_next_url(self):
        response = self.client.post(
            f"{reverse('login')}?next={reverse('locations:search')}",
            {"email": "donor@example.com", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("locations:search"))

    def test_login_ignores_unsafe_next_url(self):
        response = self.client.post(
            f"{reverse('login')}?next=https://evil.example.com/",
            {"email": "donor@example.com", "password": "StrongPass123!"},
            follow=True,
        )

        self.assertEqual(response.request["PATH_INFO"], reverse("donor_dashboard"))

    def test_home_page_logout_is_a_post_form(self):
        self.client.force_login(self.donor)

        response = self.client.get(reverse("home"))

        self.assertContains(response, 'method="post" action="/logout/"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_admin_user_page_shows_donor_fields(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="StrongPass123!",
        )
        self.client.force_login(admin)

        response = self.client.get(
            reverse("admin:accounts_user_change", args=[self.donor.pk])
        )

        self.assertContains(response, 'name="blood_type"')
        self.assertContains(response, 'name="is_available"')


# 8. Demo accounts command

class DemoAccountsCommandTests(TestCase):

    def run_command(self):
        from io import StringIO
        from django.core.management import call_command

        call_command("create_demo_accounts", stdout=StringIO())

    def test_creates_accounts_for_every_role(self):
        with self.settings(DEBUG=True):
            self.run_command()

        self.assertTrue(User.objects.get(email="admin@ehda.test").is_superuser)
        self.assertEqual(User.objects.get(email="hospital@ehda.test").role, "HOSPITAL")
        donor = User.objects.get(email="donor@ehda.test")
        self.assertTrue(donor.check_password("EhdaDemo2026!"))
        self.assertTrue(DonorLocation.objects.filter(user=donor).exists())

    def test_running_twice_does_not_duplicate(self):
        with self.settings(DEBUG=True):
            self.run_command()
            count = User.objects.count()
            self.run_command()

        self.assertEqual(User.objects.count(), count)

    def test_refuses_when_debug_is_off(self):
        from django.core.management.base import CommandError

        with self.settings(DEBUG=False), self.assertRaises(CommandError):
            self.run_command()

        self.assertFalse(User.objects.filter(email__endswith="@ehda.test").exists())
