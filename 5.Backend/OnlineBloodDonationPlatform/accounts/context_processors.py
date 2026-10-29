from .donor_requests import unanswered_count
from .models import User


def donor_requests(request):
    """Unanswered matching requests, for the donor navbar badge (#011)."""
    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated or user.role != User.Role.DONOR:
        return {}

    return {"donor_request_count": unanswered_count(user)}
