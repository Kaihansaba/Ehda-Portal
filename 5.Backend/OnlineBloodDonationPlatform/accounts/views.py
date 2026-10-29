
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from locations.search import searchable_donors
from locations.utils import public_name

from .forms import RegistrationForm, DonorProfileForm, BloodRequestForm
from .donor_requests import can_see_requests, requests_for_donor, responses_by_request
from .messaging import get_conversation
from .models import User, Donation, BloodRequest, DonorResponse, Message, Notification
from .notifications import (
    notify_account_status,
    notify_donor_response,
    notify_new_message,
    notify_new_request,
    notify_status_change,
)


def index(request):
    if request.user.is_authenticated:
        return redirect("role_redirect")

    return redirect("login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created. Please sign in.")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            # The login form posts back to the same URL, so a ?next=
            # added by @login_required is still in the query string.
            next_url = request.POST.get("next") or request.GET.get("next")

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("role_redirect")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid email or password."},
        )

    return render(request, "accounts/login.html")


@login_required
def role_redirect(request):
    if request.user.role == "DONOR":
        return redirect("donor_dashboard")
    if request.user.role == "HOSPITAL":
        return redirect("hospital_dashboard")
    if request.user.role == "ADMIN":
        return redirect("admin_dashboard")
    return redirect("home")


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return render(
                    request,
                    "accounts/access_denied.html",
                    status=403,
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@role_required("DONOR")
def donor_dashboard(request):
    donation_count = Donation.objects.filter(donor=request.user).count()
    return render(
        request,
        "accounts/donor_dashboard.html",
        {"donation_count": donation_count},
    )


@role_required("DONOR")
def donor_blood_requests(request):
    blood_requests = list(requests_for_donor(request.user))
    my_responses = responses_by_request(request.user, blood_requests)

    for blood_request in blood_requests:
        blood_request.my_response = my_responses.get(blood_request.pk)

    return render(
        request,
        "accounts/donor_blood_requests.html",
        {
            "blood_requests": blood_requests,
            "can_see_requests": can_see_requests(request.user),
        },
    )


@role_required("DONOR")
def respond_to_request(request, pk):
    if request.method != "POST":
        return redirect("donor_blood_requests")

    blood_request = get_object_or_404(BloodRequest, pk=pk)
    answer = request.POST.get("response")

    if answer not in DonorResponse.Answer.values:
        messages.error(request, "Please choose Accept or Decline.")
    elif blood_request.is_closed:
        messages.error(request, "This request is closed and can no longer be answered.")
    elif not requests_for_donor(request.user).filter(pk=blood_request.pk).exists():
        # Not compatible, not available, or no longer open for new answers.
        messages.error(request, "You can't answer this request.")
    else:
        previous = DonorResponse.objects.filter(blood_request=blood_request, donor=request.user).first()
        response, _ = DonorResponse.objects.update_or_create(
            blood_request=blood_request,
            donor=request.user,
            # A changed answer is new to the hospital again (badge).
            defaults={"response": answer, "seen_by_hospital": False},
        )
        if previous is None or previous.response != answer:
            notify_donor_response(response, request)
        if answer == DonorResponse.Answer.ACCEPTED:
            messages.success(request, "Thank you. The hospital can now see your name and phone number so they can contact you.")
        else:
            messages.success(request, "You declined this request. Your contact details are not shared. You can change your answer while it is open.")

    return redirect("donor_blood_requests")


@role_required("DONOR")
def donor_profile(request):
    if request.method == "POST":
        form = DonorProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("donor_profile")
    else:
        form = DonorProfileForm(instance=request.user)

    return render(
        request,
        "accounts/donor_profile.html",
        {"form": form},
    )


@role_required("DONOR")
def toggle_availability(request):
    if request.method == "POST":
        user = request.user
        user.is_available = not user.is_available
        user.save(update_fields=["is_available"])
    return redirect("donor_dashboard")


@role_required("HOSPITAL")
def hospital_dashboard(request):
    active_requests = BloodRequest.objects.filter(
        hospital=request.user,
        status__in=(BloodRequest.Status.OPEN, BloodRequest.Status.IN_REVIEW),
    ).count()
    # Distinct donors whose current answer to any of this hospital's
    # requests is Accepted (a donor who switched to Decline is not counted).
    donors_connected = (
        DonorResponse.objects.filter(
            blood_request__hospital=request.user,
            response=DonorResponse.Answer.ACCEPTED,
        )
        .values("donor")
        .distinct()
        .count()
    )
    return render(
        request,
        "accounts/hospital_dashboard.html",
        {"active_requests": active_requests, "donors_connected": donors_connected},
    )


@role_required("ADMIN")
def admin_dashboard(request):
    total_users = User.objects.count()
    donor_count = User.objects.filter(role=User.Role.DONOR).count()
    hospital_count = User.objects.filter(role=User.Role.HOSPITAL).count()
    reported_count = User.objects.filter(is_active=False).count()

    context = {
        "total_users": total_users,
        "donor_count": donor_count,
        "hospital_count": hospital_count,
        "reported_count": reported_count,
    }
    return render(request, "accounts/admin_dashboard.html", context)


@role_required("ADMIN")
def admin_manage_users(request):
    users = User.objects.order_by("role", "first_name", "last_name")
    return render(request, "accounts/admin_manage_users.html", {"users": users})


@role_required("ADMIN")
def admin_manage_hospitals(request):
    hospitals = User.objects.filter(role=User.Role.HOSPITAL).order_by("first_name", "last_name")
    return render(request, "accounts/admin_manage_hospitals.html", {"hospitals": hospitals})


@role_required("ADMIN")
def admin_reported_accounts(request):
    reported_users = User.objects.filter(is_active=False).order_by("role", "first_name", "last_name")
    return render(request, "accounts/admin_reported_accounts.html", {"reported_users": reported_users})


@role_required("ADMIN")
def admin_platform_activity(request):
    summary = {
        "total_users": User.objects.count(),
        "total_hospitals": User.objects.filter(role=User.Role.HOSPITAL).count(),
        "total_donors": User.objects.filter(role=User.Role.DONOR).count(),
        "total_requests": BloodRequest.objects.count(),
        "open_requests": BloodRequest.objects.filter(status=BloodRequest.Status.OPEN).count(),
        "in_review_requests": BloodRequest.objects.filter(status=BloodRequest.Status.IN_REVIEW).count(),
        "accepted_requests": BloodRequest.objects.filter(status=BloodRequest.Status.ACCEPTED).count(),
        "completed_requests": BloodRequest.objects.filter(status=BloodRequest.Status.COMPLETED).count(),
        "cancelled_requests": BloodRequest.objects.filter(status=BloodRequest.Status.CANCELLED).count(),
        "total_responses": DonorResponse.objects.count(),
        "accepted_responses": DonorResponse.objects.filter(response=DonorResponse.Answer.ACCEPTED).count(),
        "declined_responses": DonorResponse.objects.filter(response=DonorResponse.Answer.DECLINED).count(),
    }
    recent_requests = BloodRequest.objects.select_related("hospital").order_by("-created_at")[:10]
    return render(
        request,
        "accounts/admin_platform_activity.html",
        {"summary": summary, "recent_requests": recent_requests},
    )


@role_required("ADMIN")
def admin_platform_statistics(request):
    total_users = User.objects.count()
    total_donors = User.objects.filter(role=User.Role.DONOR).count()
    total_hospitals = User.objects.filter(role=User.Role.HOSPITAL).count()
    total_requests = BloodRequest.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    context = {
        "total_users": total_users,
        "total_donors": total_donors,
        "total_hospitals": total_hospitals,
        "total_requests": total_requests,
        "active_users": active_users,
        "inactive_users": inactive_users,
    }
    return render(request, "accounts/admin_platform_statistics.html", context)


@role_required("ADMIN")
def admin_security_access(request):
    users = User.objects.order_by("-is_active", "role", "first_name", "last_name")
    summary = {
        "total_users": users.count(),
        "active_users": users.filter(is_active=True).count(),
        "inactive_users": users.filter(is_active=False).count(),
        "admins": users.filter(role=User.Role.ADMIN).count(),
        "hospitals": users.filter(role=User.Role.HOSPITAL).count(),
        "donors": users.filter(role=User.Role.DONOR).count(),
    }
    return render(
        request,
        "accounts/admin_security_access.html",
        {"summary": summary, "users": users},
    )


# Pages that may send the admin back after a status toggle. Only these
# names are accepted, so "next" cannot redirect to another site.
TOGGLE_RETURN_PAGES = {
    "admin_manage_users",
    "admin_manage_hospitals",
    "admin_reported_accounts",
}


@role_required("ADMIN")
def toggle_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        if user == request.user:
            # Deactivating yourself would lock you out mid-session.
            messages.error(request, "You can't deactivate your own account.")
        else:
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            state = "activated" if user.is_active else "deactivated"
            messages.success(request, f"{user.email} has been {state}.")
            notify_account_status(user, request)

    redirect_name = request.POST.get("next")
    if redirect_name not in TOGGLE_RETURN_PAGES:
        redirect_name = "admin_manage_users"
    return redirect(redirect_name)


def chosen_donor(hospital, donor_id):
    """
    The donor a hospital picked in search (#010), or None. Only donors the
    hospital could find in search qualify: active, available, with a
    location set.
    """
    if not str(donor_id or "").isdigit():
        return None

    location = searchable_donors(hospital).filter(user_id=int(donor_id)).first()
    return location.user if location else None


@role_required("HOSPITAL")
def create_blood_request(request):
    donor_id = request.POST.get("target_donor") or request.GET.get("donor")
    target_donor = chosen_donor(request.user, donor_id)

    if donor_id and target_donor is None:
        messages.error(request, "That donor is no longer available. You can still send the request to all compatible donors.")

    if request.method == "POST":
        form = BloodRequestForm(request.POST, target_donor=target_donor)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.hospital = request.user
            blood_request.target_donor = target_donor
            blood_request.save()
            notify_new_request(blood_request, request)
            if target_donor:
                # public_name ends with "." when it has an initial ("Dina D.").
                name = public_name(target_donor)
                messages.success(request, f"Your blood request has been sent to {name}{'' if name.endswith('.') else '.'}")
            else:
                messages.success(request, "Your blood request has been created. Compatible available donors can now see it.")
            return redirect("manage_blood_requests")
    else:
        initial = {"blood_type": target_donor.blood_type} if target_donor else {}
        form = BloodRequestForm(initial=initial, target_donor=target_donor)

    return render(
        request,
        "accounts/create_blood_request.html",
        {"form": form, "target_donor": target_donor},
    )


@role_required("HOSPITAL")
def manage_blood_requests(request):
    requests = BloodRequest.objects.filter(
        hospital=request.user
    ).order_by("-created_at")
    return render(
        request,
        "accounts/manage_blood_requests.html",
        {"requests": requests},
    )


def blood_request_error_page(request, exc):
    """The request list again, with the reason a status change failed."""
    return render(
        request,
        "accounts/manage_blood_requests.html",
        {
            "requests": BloodRequest.objects.filter(hospital=request.user).order_by("-created_at"),
            "error": " ".join(exc.messages),
        },
    )


@role_required("HOSPITAL")
def request_detail(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, hospital=request.user)

    # Opening the request marks new acceptances as seen (navbar badge).
    # Remember which were new so the page can still highlight them.
    new_acceptances = blood_request.responses.filter(
        response=DonorResponse.Answer.ACCEPTED, seen_by_hospital=False,
    )
    new_response_ids = list(new_acceptances.values_list("pk", flat=True))
    new_acceptances.update(seen_by_hospital=True)

    # "blood_request", not "request": that name would hide Django's request
    # object from the navbar and base template.
    return render(
        request,
        "accounts/request_detail.html",
        {"blood_request": blood_request, "new_response_ids": new_response_ids},
    )


@role_required("HOSPITAL")
def change_request_status(request, pk, status):
    blood_request = get_object_or_404(BloodRequest, pk=pk, hospital=request.user)

    if request.method != "POST":
        return redirect("manage_blood_requests")

    try:
        blood_request.update_status(status)
    except ValidationError as exc:
        return blood_request_error_page(request, exc)

    notify_status_change(blood_request, request)
    return redirect("manage_blood_requests")


@role_required("HOSPITAL")
def close_blood_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, hospital=request.user)

    if request.method != "POST":
        return redirect("manage_blood_requests")

    new_status = request.POST.get("status")
    valid_statuses = {
        BloodRequest.Status.COMPLETED,
        BloodRequest.Status.CANCELLED,
    }

    if new_status not in valid_statuses:
        return redirect("manage_blood_requests")

    try:
        blood_request.update_status(new_status)
    except ValidationError as exc:
        return blood_request_error_page(request, exc)

    notify_status_change(blood_request, request)
    return redirect("manage_blood_requests")


@login_required
def home(request):
    return render(request, "accounts/home.html")


def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("role_redirect")


@role_required("DONOR")
def donation_history(request):
    donations = Donation.objects.filter(
        donor=request.user
    ).order_by("-donation_date")
    return render(
        request,
        "accounts/donation_history.html",
        {"donations": donations},
    )


def is_safe_internal_path(link):
    """Only paths on this site, e.g. "/dashboard/" (never "//evil.com")."""
    return link.startswith("/") and not link.startswith("//") and "\\" not in link


@login_required
def notifications(request):
    items = request.user.notifications.all()[:50]
    return render(request, "accounts/notifications.html", {"notifications": items})


@login_required
def open_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if not notification.read:
        notification.read = True
        notification.save(update_fields=["read"])

    if notification.link and is_safe_internal_path(notification.link):
        return redirect(notification.link)
    return redirect("notifications")


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        updated = request.user.notifications.filter(read=False).update(read=True)
        if updated:
            messages.success(request, "All notifications are marked as read.")
    return redirect("notifications")


MAX_MESSAGE_LENGTH = 2000


@role_required("DONOR", "HOSPITAL")
def conversation(request, pk, donor_pk):
    convo = get_conversation(request.user, pk, donor_pk)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()

        if not convo.can_send:
            messages.error(request, convo.read_only_reason)
        elif not body:
            messages.error(request, "Please write a message first.")
        elif len(body) > MAX_MESSAGE_LENGTH:
            messages.error(request, f"Messages can be at most {MAX_MESSAGE_LENGTH} characters.")
        else:
            message = Message.objects.create(
                blood_request=convo.blood_request, donor=convo.donor, sender=request.user, body=body,
            )
            notify_new_message(message, convo.other_party, request)
        return redirect("conversation", pk=pk, donor_pk=donor_pk)

    return render(request, "accounts/conversation.html", {"convo": convo})


@role_required("DONOR", "HOSPITAL")
def conversation_messages(request, pk, donor_pk):
    """The message list only, for the page's 10-second refresh."""
    convo = get_conversation(request.user, pk, donor_pk)
    return render(request, "partials/message_list.html", {"convo": convo})
