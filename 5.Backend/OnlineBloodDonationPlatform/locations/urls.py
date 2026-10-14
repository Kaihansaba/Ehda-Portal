from django.urls import path

from . import views


app_name = "locations"

urlpatterns = [
    # Donor sets their (private) location
    path(
        "dashboard/donor/location/",
        views.donor_location,
        name="donor_location",
    ),
]
