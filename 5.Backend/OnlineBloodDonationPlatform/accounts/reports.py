"""
Who may report whom (#019).

Reports come from places where people deal with each other: blood
requests and conversations. A donor and a hospital may report each other
if the donor answered one of the hospital's requests, was sent one
directly, or they have exchanged messages. Nobody can report themselves
or an administrator.
"""

from locations.utils import public_name

from .models import BloodRequest, DonorResponse, Message, User


def have_interacted(user, other):
    if user.role == User.Role.DONOR and other.role == User.Role.HOSPITAL:
        donor, hospital = user, other
    elif user.role == User.Role.HOSPITAL and other.role == User.Role.DONOR:
        donor, hospital = other, user
    else:
        return False

    return (
        DonorResponse.objects.filter(donor=donor, blood_request__hospital=hospital).exists()
        or BloodRequest.objects.filter(hospital=hospital, target_donor=donor).exists()
        or Message.objects.filter(donor=donor, blood_request__hospital=hospital).exists()
    )


def can_report(user, other):
    return user != other and other.role != User.Role.ADMIN and have_interacted(user, other)


def display_name(user):
    """How a reported account is named to the reporter (#009 for donors)."""
    if user.role == User.Role.DONOR:
        return public_name(user)
    return user.get_full_name() or "this hospital"
