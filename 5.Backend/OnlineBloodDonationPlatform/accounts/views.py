
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegistrationForm, DonorProfileForm, BloodRequestForm
from .models import User, Donation, BloodRequest


def index(request):
    if request.user.is_authenticated:
        return redirect("role_redirect")

    return redirect("login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
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
        return decorator_wrapper(wrapper)
    return decorator


def decorator_wrapper(view_func):
    return view_func


@role_required("DONOR")
def donor_dashboard(request):
    donation_count = Donation.objects.filter(donor=request.user).count()
    return render(
        request,
        "accounts/donor_dashboard.html",
        {"donation_count": donation_count},
    )


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
    return render(request, "accounts/hospital_dashboard.html")


@role_required("ADMIN")
def admin_dashboard(request):
    total_users = User.objects.count()
    donors = User.objects.filter(role="DONOR").count()
    hospitals = User.objects.filter(role="HOSPITAL").count()

    context = {
        "total_users": total_users,
        "donors": donors,
        "hospitals": hospitals,
        "reports": 0,
    }

    return render(request, "accounts/admin_dashboard.html", context)


@role_required("HOSPITAL")
def create_blood_request(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.hospital = request.user
            blood_request.save()
            return redirect("manage_blood_requests")
    else:
        form = BloodRequestForm()

    return render(
        request,
        "accounts/create_blood_request.html",
        {"form": form},
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
