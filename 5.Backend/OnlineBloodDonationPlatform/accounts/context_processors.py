from .donor_requests import new_acceptances_count, unanswered_count
from .models import User


def request_badges(request):
    """
    Counts for the navbar and dashboard badges:
    donors - matching requests they haven't answered (#011);
    hospitals - accepted responses they haven't seen yet.
    """
    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated:
        return {}

    if user.role == User.Role.DONOR:
        return {"donor_request_count": unanswered_count(user)}

    if user.role == User.Role.HOSPITAL:
        return {"hospital_new_accepted_count": new_acceptances_count(user)}

    return {}
