from django.contrib import admin
from django.urls import include, path, reverse_lazy
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
    donor_blood_requests,
    respond_to_request,
    toggle_availability,
    hospital_dashboard,
    admin_dashboard,
    admin_manage_users,
    admin_manage_hospitals,
    admin_reported_accounts,
    admin_platform_activity,
    admin_platform_statistics,
    admin_security_access,
    toggle_user_status,
    create_blood_request,
    manage_blood_requests,
    request_detail,
    change_request_status,
    close_blood_request,
)


# Django admin branding (templates/admin/base_site.html adds the logo)
admin.site.site_header = "Ehda Admin"
admin.site.site_title = "Ehda Admin"
admin.site.index_title = "Platform management"

# "View site" in the admin goes to the user's own dashboard.
admin.site.site_url = reverse_lazy("role_redirect")


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
    path(
        "dashboard/donor/requests/",
        donor_blood_requests,
        name="donor_blood_requests",
    ),
    path(
        "dashboard/donor/requests/<int:pk>/respond/",
        respond_to_request,
        name="respond_to_request",
    ),
    path("dashboard/hospital/", hospital_dashboard, name="hospital_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),

    # Admin tools (Developer 3)
    path(
        "dashboard/admin/users/",
        admin_manage_users,
        name="admin_manage_users",
    ),
    path(
        "dashboard/admin/hospitals/",
        admin_manage_hospitals,
        name="admin_manage_hospitals",
    ),
    path(
        "dashboard/admin/reported-accounts/",
        admin_reported_accounts,
        name="admin_reported_accounts",
    ),
    path(
        "dashboard/admin/activity/",
        admin_platform_activity,
        name="admin_platform_activity",
    ),
    path(
        "dashboard/admin/statistics/",
        admin_platform_statistics,
        name="admin_platform_statistics",
    ),
    path(
        "dashboard/admin/security/",
        admin_security_access,
        name="admin_security_access",
    ),
    path(
        "dashboard/admin/users/<int:pk>/toggle-status/",
        toggle_user_status,
        name="toggle_user_status",
    ),

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
    path(
        "dashboard/hospital/requests/<int:pk>/",
        request_detail,
        name="request_detail",
    ),
    path(
        "dashboard/hospital/requests/<int:pk>/status/<str:status>/",
        change_request_status,
        name="change_request_status",
    ),
    path(
        "dashboard/hospital/requests/<int:pk>/close/",
        close_blood_request,
        name="close_blood_request",
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
