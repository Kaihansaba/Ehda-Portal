import math

from .constants import APPROXIMATE_DECIMALS, COMPATIBLE_DONORS


EARTH_RADIUS_KM = 6371.0088

# Length of one degree of latitude in km (almost constant).
KM_PER_DEGREE_LAT = 111.32


def approximate(latitude, longitude):
    """Round a point to about 1 km so a donor's exact spot is hidden."""
    return (
        round(float(latitude), APPROXIMATE_DECIMALS),
        round(float(longitude), APPROXIMATE_DECIMALS),
    )


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in km."""
    lat1, lng1, lat2, lng2 = map(
        math.radians,
        (float(lat1), float(lng1), float(lat2), float(lng2)),
    )

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def bounding_box(latitude, longitude, radius_km):
    """
    A lat/lng box that contains every point within radius_km.

    SQLite has no geo functions, so we use this box as a cheap database
    prefilter, then compute the real distance in Python.
    Returns (min_lat, max_lat, min_lng, max_lng).
    """
    latitude = float(latitude)
    longitude = float(longitude)

    lat_delta = radius_km / KM_PER_DEGREE_LAT

    # Degrees of longitude get shorter towards the poles.
    cos_lat = max(math.cos(math.radians(latitude)), 0.01)
    lng_delta = radius_km / (KM_PER_DEGREE_LAT * cos_lat)

    return (
        latitude - lat_delta,
        latitude + lat_delta,
        longitude - lng_delta,
        longitude + lng_delta,
    )


def compatible_donor_types(recipient_blood_type):
    """Blood types a recipient can safely receive (ABO/Rh red cells)."""
    return COMPATIBLE_DONORS.get(recipient_blood_type, [recipient_blood_type])


def describe_distance(distance_km):
    """Human friendly, deliberately rounded distance."""
    if distance_km is None:
        return ""

    if distance_km < 1:
        return "less than 1 km"

    return f"about {round(distance_km)} km"


def public_name(user):
    """First name and last initial only, e.g. "Ahmad S."."""
    if user.last_name:
        return f"{user.first_name} {user.last_name[0].upper()}."

    return user.first_name
