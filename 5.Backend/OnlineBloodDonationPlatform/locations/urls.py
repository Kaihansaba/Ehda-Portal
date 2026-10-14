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

    # Search donors by blood type and location (#006, #007)
    path("search/", views.donor_search, name="search"),

    # Map of donors, hospitals and donation centres (#008)
    path("map/", views.donor_map, name="map"),
]
