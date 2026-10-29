"""
Which blood requests a donor sees and may answer (#011, #012).

A donor sees open or in-review requests for a blood type they can give
to (locations.constants.COMPATIBLE_DONORS), plus any request they have
already answered that is not yet completed or cancelled, so they can
still change their answer. Unavailable donors and donors without a
blood type see nothing.
"""
from django.db.models import Q

from locations.constants import COMPATIBLE_DONORS

from .models import BloodRequest, DonorResponse, User


# Statuses that new answers can come in for.
NEW_REQUEST_STATUSES = (BloodRequest.Status.OPEN, BloodRequest.Status.IN_REVIEW)


def recipient_types_for(donor_blood_type):
    """Blood types of requests this donor's blood can be given to."""
    return [
        recipient
        for recipient, donors in COMPATIBLE_DONORS.items()
        if donor_blood_type in donors
    ]


def can_see_requests(donor):
    return donor.role == User.Role.DONOR and donor.is_available and bool(donor.blood_type)


def requests_for_donor(donor):
    """Requests shown on the donor's Blood requests page, newest first."""
    if not can_see_requests(donor):
        return BloodRequest.objects.none()

    new_matches = Q(
        status__in=NEW_REQUEST_STATUSES,
        blood_type__in=recipient_types_for(donor.blood_type),
    )
    already_answered = Q(responses__donor=donor) & ~Q(status__in=BloodRequest.CLOSED_STATUSES)

    return (
        BloodRequest.objects.filter(new_matches | already_answered)
        .select_related("hospital")
        .distinct()
        .order_by("-created_at")
    )


def unanswered_count(donor):
    """New matching requests the donor hasn't answered (the in-app notification)."""
    if not can_see_requests(donor):
        return 0

    return (
        BloodRequest.objects.filter(
            status__in=NEW_REQUEST_STATUSES,
            blood_type__in=recipient_types_for(donor.blood_type),
        )
        .exclude(responses__donor=donor)
        .count()
    )


def responses_by_request(donor, blood_requests):
    """{request id: the donor's DonorResponse} for the given requests."""
    responses = DonorResponse.objects.filter(donor=donor, blood_request__in=blood_requests)
    return {response.blood_request_id: response for response in responses}
