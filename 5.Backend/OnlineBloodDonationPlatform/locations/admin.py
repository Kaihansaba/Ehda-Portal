from django.contrib import admin

from .models import DonorLocation, Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "facility_type",
        "province",
        "district",
        "phone",
        "is_active",
    )

    list_filter = (
        "facility_type",
        "province",
        "is_active",
    )

    search_fields = (
        "name",
        "district",
        "address",
    )


@admin.register(DonorLocation)
class DonorLocationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "province",
        "district",
        "updated_at",
    )

    list_filter = (
        "province",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "district",
    )

    readonly_fields = (
        "updated_at",
    )
