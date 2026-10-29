"""
Conversations between a hospital and a donor about a blood request (#014).

A conversation exists for every donor who answered a request. Only the
hospital that owns the request and that donor can open it. Messages can
be sent only while the donor's answer is Accepted and the request is not
completed or cancelled; otherwise the history is read-only.
"""
from django.http import Http404
from django.shortcuts import get_object_or_404

from locations.utils import public_name

from .models import BloodRequest, DonorResponse, User


class Conversation:

    def __init__(self, blood_request, donor, response, viewer):
        self.blood_request = blood_request
        self.donor = donor
        self.response = response
        self.viewer = viewer

    @property
    def hospital(self):
        return self.blood_request.hospital

    @property
    def other_party(self):
        return self.donor if self.viewer == self.hospital else self.hospital

    def name_of(self, user):
        """
        How a participant is named on the page. PRIVACY (#009): a donor's
        full name only while they have accepted; otherwise "Dina D.".
        """
        if user == self.hospital:
            return self.hospital.get_full_name() or "The hospital"
        if self.response.shares_contact:
            return self.donor.get_full_name()
        return public_name(self.donor)

    @property
    def other_party_name(self):
        return self.name_of(self.other_party)

    @property
    def can_send(self):
        return self.response.can_message

    @property
    def messages(self):
        return self.blood_request.messages.filter(donor=self.donor).select_related("sender")

    @property
    def read_only_reason(self):
        if self.blood_request.is_closed:
            return f"This request is {self.blood_request.get_status_display().lower()}, so the conversation is closed."
        if self.response.response != DonorResponse.Answer.ACCEPTED:
            return "The donor declined this request, so messaging is closed. Earlier messages stay visible."
        return ""


def get_conversation(user, request_pk, donor_pk):
    """The conversation, or 404 if it doesn't exist or isn't the user's."""
    blood_request = get_object_or_404(BloodRequest.objects.select_related("hospital"), pk=request_pk)
    donor = get_object_or_404(User, pk=donor_pk, role=User.Role.DONOR)

    if user != blood_request.hospital and user != donor:
        raise Http404("No such conversation.")

    response = DonorResponse.objects.filter(blood_request=blood_request, donor=donor).first()
    if response is None:
        raise Http404("No such conversation.")

    return Conversation(blood_request, donor, response, user)
