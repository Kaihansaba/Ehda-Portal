from dataclasses import dataclass

from accounts.models import User

from .constants import APPROXIMATE_DECIMALS
from .models import DonorLocation
from .utils import (
    bounding_box,
    compatible_donor_types,
    describe_distance,
    haversine_km,
    public_name,
)


# Approximate coordinates can be up to half a rounding step away from the
# exact point, so the database prefilter box is widened by this much.
ROUNDING_MARGIN_DEGREES = 10 ** -APPROXIMATE_DECIMALS


@dataclass
class DonorResult:
    """
    What a searcher is allowed to see about a donor.

    PRIVACY: no email, phone, last name or exact coordinates.
    """

    donor_id: int
    name: str
    blood_type: str
    is_available: bool
    province: str
    district: str
    distance_km: float | None

    @property
    def distance_label(self):
        return describe_distance(self.distance_km)


def searchable_donors(searcher):
    """Active, available donors who have set a location, minus the searcher."""
    return (
        DonorLocation.objects
        .select_related("user")
        .filter(
            user__role=User.Role.DONOR,
            user__is_active=True,
            user__is_available=True,
        )
        .exclude(user=searcher)
    )


def search_donors(
    searcher,
    blood_type,
    include_compatible=False,
    origin=None,
    radius_km=None,
    province="",
    district="",
):
    """
    Find donors for a blood type.

    origin is a (lat, lng) tuple. When given, results are sorted by
    distance and radius_km (if set) limits how far away donors may be.
    Distances are measured to the donor's APPROXIMATE location, so the
    results never reveal more than the ~1 km area shown on the map.
    """
    if include_compatible:
        blood_types = compatible_donor_types(blood_type)
    else:
        blood_types = [blood_type]

    locations = searchable_donors(searcher).filter(
        user__blood_type__in=blood_types
    )

    if province:
        locations = locations.filter(province=province)

    if district:
        # Donors who hide their area (#003) never match a district search.
        locations = locations.filter(district__icontains=district, user__show_district=True)

    if origin is not None and radius_km:
        min_lat, max_lat, min_lng, max_lng = bounding_box(
            origin[0], origin[1], radius_km
        )

        locations = locations.filter(
            latitude__gte=min_lat - ROUNDING_MARGIN_DEGREES,
            latitude__lte=max_lat + ROUNDING_MARGIN_DEGREES,
            longitude__gte=min_lng - ROUNDING_MARGIN_DEGREES,
            longitude__lte=max_lng + ROUNDING_MARGIN_DEGREES,
        )

    results = []

    for location in locations:
        distance_km = None

        if origin is not None:
            approx_lat, approx_lng = location.approximate_coordinates
            distance_km = haversine_km(
                origin[0], origin[1], approx_lat, approx_lng
            )

            if radius_km and distance_km > radius_km:
                continue

        user = location.user

        results.append(
            DonorResult(
                donor_id=user.pk,
                name=public_name(user),
                blood_type=user.blood_type,
                is_available=user.is_available,
                province=location.get_province_display(),
                district=location.district if user.show_district else "",
                distance_km=distance_km,
            )
        )

    if origin is not None:
        results.sort(key=lambda result: result.distance_km)
    else:
        results.sort(key=lambda result: (result.province, result.name))

    return results
