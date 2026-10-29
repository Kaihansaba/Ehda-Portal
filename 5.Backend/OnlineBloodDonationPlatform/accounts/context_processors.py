from .donor_requests import new_acceptances_count, unanswered_count
from .models import User


def request_badges(request):
    """
    Counts for the navbar and dashboard badges:
    donors - matching requests they haven't answered (#011);
    hospitals - accepted responses they haven't seen yet;
    everyone - unread notifications (#011).
    """
    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated:
        return {}

    badges = {"unread_notification_count": user.notifications.filter(read=False).count()}

    if user.role == User.Role.DONOR:
        badges["donor_request_count"] = unanswered_count(user)

    if user.role == User.Role.HOSPITAL:
        badges["hospital_new_accepted_count"] = new_acceptances_count(user)

    return badges
