from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import RegistrationForm, DonorProfileForm, BloodRequestForm
from .models import BloodRequest, User


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

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is not None:
            login(request, user)
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
    elif request.user.role == "HOSPITAL":
        return redirect("hospital_dashboard")
    elif request.user.role == "ADMIN":
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
    return render(request, "accounts/donor_dashboard.html")


@role_required("DONOR")
def donor_profile(request):
    if request.method == "POST":
        form = DonorProfileForm(
            request.POST,
            instance=request.user,
        )

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


@role_required("ADMIN")
def toggle_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

    redirect_name = request.POST.get("next") or "admin_manage_users"
    return redirect(redirect_name)


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

    return render(request, "accounts/create_blood_request.html", {"form": form})


@role_required("HOSPITAL")
def manage_blood_requests(request):
    requests = BloodRequest.objects.filter(hospital=request.user).order_by("-created_at")
    return render(
        request,
        "accounts/manage_blood_requests.html",
        {"requests": requests},
    )


@role_required("HOSPITAL")
def close_blood_request(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk, hospital=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = {
            BloodRequest.Status.COMPLETED,
            BloodRequest.Status.CANCELLED,
        }

        if new_status in valid_statuses:
            blood_request.status = new_status
            blood_request.save(update_fields=["status"])

    return redirect("manage_blood_requests")


@login_required
def home(request):
    return render(request, "accounts/home.html")


def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("role_redirect")
