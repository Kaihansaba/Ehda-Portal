from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse_lazy

from .models import User, Donation


admin.site.site_url = reverse_lazy("role_redirect")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
                "blood_type",
                "is_available",
    )

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "password",
            )
        }),

        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "phone",
            )
        }),

        ("Donor Information", {
            "fields": (
                "blood_type",
                "is_available",
            )
        }),

        ("Role & Permissions", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
            )
        }),
    )

    readonly_fields = (
        "date_joined",
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "phone",
                "blood_type",
                "is_available",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "donation_date", "blood_type", "notes")
    list_filter = ("blood_type", "donation_date")
    search_fields = ("donor__email", "donor__first_name", "donor__last_name")
