from django.contrib import messages
from django.shortcuts import render, redirect

from accounts.views import role_required

from .constants import AFGHANISTAN_CENTER, PROVINCES
from .forms import DonorLocationForm
from .models import DonorLocation


def province_centres():
    """Province name -> {lat, lng}, for moving the map in templates."""
    return {
        name: {"lat": lat, "lng": lng}
        for name, (lat, lng) in PROVINCES.items()
    }


def map_center_for(user):
    """Centre on the user's approximate location, else on Afghanistan."""
    location = DonorLocation.objects.filter(user=user).first()

    if location is None:
        return AFGHANISTAN_CENTER

    lat, lng = location.approximate_coordinates
    return {"lat": lat, "lng": lng, "zoom": 12}


@role_required("DONOR")
def donor_location(request):
    location = DonorLocation.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = DonorLocationForm(request.POST, instance=location)

        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            location.save()

            messages.success(request, "Your location has been saved.")
            return redirect("locations:donor_location")
    else:
        form = DonorLocationForm(instance=location)

    current_area = None
    if location is not None:
        lat, lng = location.approximate_coordinates
        current_area = {"lat": lat, "lng": lng}

    return render(
        request,
        "locations/donor_location.html",
        {
            "form": form,
            "has_location": location is not None,
            "current_area": current_area,
            "map_center": map_center_for(request.user),
            "province_centres": province_centres(),
        },
    )
