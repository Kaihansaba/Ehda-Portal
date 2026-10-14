from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import NoReverseMatch, reverse

from accounts.views import role_required

from .constants import AFGHANISTAN_CENTER, DONOR_SEARCH_ROLES, PROVINCES
from .forms import DonorLocationForm, DonorSearchForm
from .models import DonorLocation
from .search import search_donors


def blood_request_url(donor_id):
    """
    Link for the "Send request" button.

    TODO(#010, Developer 3): the `requests:create` route does not exist
    yet. Until it does, this returns None and the button is disabled.
    """
    try:
        return reverse("requests:create", args=[donor_id])
    except NoReverseMatch:
        return None


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


@role_required(*DONOR_SEARCH_ROLES)
def donor_search(request):
    form = DonorSearchForm(request.GET or None)
    results = None

    if form.is_bound and form.is_valid():
        results = search_donors(
            searcher=request.user,
            blood_type=form.cleaned_data["blood_type"],
            include_compatible=form.cleaned_data["include_compatible"],
            origin=form.origin,
            radius_km=form.radius_km,
            province=form.cleaned_data["province"],
            district=form.cleaned_data["district"].strip(),
        )

        for result in results:
            result.request_url = blood_request_url(result.donor_id)

    return render(
        request,
        "locations/search.html",
        {
            "form": form,
            "results": results,
            "map_center": map_center_for(request.user),
            "province_centres": province_centres(),
        },
    )
