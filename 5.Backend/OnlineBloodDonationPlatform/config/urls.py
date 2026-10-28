from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

from accounts.views import (
    index,
    home,
    register,
    user_login,
    user_logout,
    role_redirect,
    donor_dashboard,
    donor_profile,
    donation_history,
    toggle_availability,
    hospital_dashboard,
    admin_dashboard,
    create_blood_request,
    manage_blood_requests,
)


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Site root: dashboard if logged in, otherwise login
    path("", index, name="index"),

    # Authentication and home
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("home/", home, name="home"),

    # Dashboards
    path("dashboard/", role_redirect, name="role_redirect"),
    path("dashboard/donor/", donor_dashboard, name="donor_dashboard"),
    path(
        "dashboard/donor/profile/",
        donor_profile,
        name="donor_profile",
    ),
    path(
        "dashboard/donor/donations/",
        donation_history,
        name="donation_history",
    ),
    path(
        "dashboard/donor/availability/",
        toggle_availability,
        name="toggle_availability",
    ),
    path("dashboard/hospital/", hospital_dashboard, name="hospital_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),

    # Hospital blood requests
    path(
        "dashboard/hospital/requests/",
        manage_blood_requests,
        name="manage_blood_requests",
    ),
    path(
        "dashboard/hospital/requests/new/",
        create_blood_request,
        name="create_blood_request",
    ),

    # Donor location, search and map (Developer 2)
    path("", include("locations.urls")),

    # Password reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
