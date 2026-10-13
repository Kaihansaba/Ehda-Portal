from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from accounts.views import (
    register,
    user_login,
    home,
    user_logout,
    role_redirect,
    donor_dashboard,
    donor_profile,
    toggle_availability,
    hospital_dashboard,
    admin_dashboard,
)


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),

    # Home
    path("home/", home, name="home"),

    # Role-based dashboard redirect
    path("dashboard/", role_redirect, name="role_redirect"),

    # Donor dashboard
    path("dashboard/donor/", donor_dashboard, name="donor_dashboard"),

    # Donor profile and availability
    path(
        "dashboard/donor/profile/",
        donor_profile,
        name="donor_profile",
    ),
    path(
        "dashboard/donor/availability/",
        toggle_availability,
        name="toggle_availability",
    ),

    # Hospital dashboard
    path(
        "dashboard/hospital/",
        hospital_dashboard,
        name="hospital_dashboard",
    ),

    # Admin dashboard
    path(
        "dashboard/admin/",
        admin_dashboard,
        name="admin_dashboard",
    ),

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

    # Password reset email sent page
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    # New password page
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    # Password reset completed page
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]