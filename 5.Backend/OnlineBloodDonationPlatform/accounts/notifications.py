"""
In-app notifications, also sent by email (#011).

Email uses the EMAIL_* settings: without SMTP settings in .env it is
printed in the terminal running the server. Sending is best-effort: a
failure is logged and never stops the page that triggered it.
"""
import logging

from django.core.mail import send_mail
from django.urls import reverse

from locations.utils import compatible_donor_types, public_name

from .models import BloodRequest, DonorResponse, Notification, User


logger = logging.getLogger(__name__)


def notify(user, message, link="", request=None):
    """Create an in-app notification for user and email it to them."""
    notification = Notification.objects.create(user=user, message=message, link=link)
    send_notification_email(user, message, link, request)
    return notification


def send_notification_email(user, message, link="", request=None):
    if not user.email:
        return

    url = request.build_absolute_uri(link) if (request and link) else link
    body = message + (f"\n\nOpen Ehda Portal: {url}" if url else "") + "\n\n- Ehda Portal"

    try:
        send_mail(f"Ehda Portal: {message[:80]}", body, None, [user.email])
    except Exception:
        # Email is a convenience; the in-app notification is already saved.
        logger.exception("Could not send notification email to user %s", user.pk)


def describe(blood_request):
    """'2 units of A+' for messages."""
    units = blood_request.units_needed
    return f"{units} unit{'s' if units != 1 else ''} of {blood_request.blood_type}"


def donors_for_new_request(blood_request):
    """Donors who will see a new request on their Blood requests page."""
    if blood_request.target_donor_id:
        donors = User.objects.filter(pk=blood_request.target_donor_id)
    else:
        donors = User.objects.filter(blood_type__in=compatible_donor_types(blood_request.blood_type))

    return donors.filter(role=User.Role.DONOR, is_active=True, is_available=True).exclude(blood_type="")


def notify_new_request(blood_request, request=None):
    hospital = blood_request.hospital.get_full_name() or "A hospital"
    urgency = "" if blood_request.urgency == BloodRequest.Urgency.ROUTINE else f" ({blood_request.get_urgency_display()})"
    sent_to_you = " It was sent to you specifically." if blood_request.target_donor_id else ""
    message = f"{hospital} needs {describe(blood_request)}{urgency}.{sent_to_you}"
    link = reverse("donor_blood_requests")

    for donor in donors_for_new_request(blood_request):
        notify(donor, message, link, request)


def notify_donor_response(response, request=None):
    verb = "accepted" if response.response == DonorResponse.Answer.ACCEPTED else "declined"
    message = f"{public_name(response.donor)} {verb} your request for {describe(response.blood_request)}."
    link = reverse("request_detail", args=[response.blood_request_id])
    notify(response.blood_request.hospital, message, link, request)


def notify_status_change(blood_request, request=None):
    """Tell the donors involved (everyone who answered, and the target)."""
    hospital = blood_request.hospital.get_full_name() or "the hospital"
    message = (
        f"The request from {hospital} for {describe(blood_request)} "
        f"is now {blood_request.get_status_display()}."
    )
    link = reverse("donor_blood_requests")

    donor_ids = set(blood_request.responses.values_list("donor_id", flat=True))
    if blood_request.target_donor_id:
        donor_ids.add(blood_request.target_donor_id)

    for donor in User.objects.filter(pk__in=donor_ids, is_active=True):
        notify(donor, message, link, request)


def notify_account_status(user, request=None):
    if user.is_active:
        notify(user, "Your Ehda account has been reactivated. You can sign in again.", reverse("login"), request)
    else:
        notify(user, "Your Ehda account has been deactivated by an administrator.", "", request)


def notify_new_message(message, recipient, request=None):
    sender = message.sender
    if sender.role == User.Role.DONOR:
        name = public_name(sender)
    else:
        name = sender.get_full_name() or "The hospital"
    text = f"New message from {name} about the request for {describe(message.blood_request)}."
    link = reverse("conversation", args=[message.blood_request_id, message.donor_id])
    notify(recipient, text, link, request)
