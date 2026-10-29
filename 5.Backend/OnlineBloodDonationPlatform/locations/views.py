from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import User
from accounts.views import role_required

from .constants import AFGHANISTAN_CENTER, DONOR_SEARCH_ROLES, PROVINCES
from .forms import DonorLocationForm, DonorSearchForm
from .models import DonorLocation, Facility
from .search import search_donors, searchable_donors
from .utils import public_name


def blood_request_url(searcher, donor_id):
    """
    Link for the "Send request" button (#010): the new-request form,
    targeted at this donor. Only hospitals send requests; for other roles
    this returns None and the button is not shown.
    """
    if searcher.role != User.Role.HOSPITAL:
        return None
    return f"{reverse('create_blood_request')}?donor={donor_id}"


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
            result.request_url = blood_request_url(request.user, result.donor_id)

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


@role_required(*DONOR_SEARCH_ROLES)
def donor_map(request):
    blood_type = request.GET.get("blood_type", "")
    if blood_type not in User.BloodType.values:
        blood_type = ""

    locations = searchable_donors(request.user)
    if blood_type:
        locations = locations.filter(user__blood_type=blood_type)

    # PRIVACY: donors are sent with approximate coordinates only.
    donors = []
    for location in locations:
        lat, lng = location.approximate_coordinates
        donors.append({
            "name": public_name(location.user),
            "blood_type": location.user.blood_type,
            "lat": lat,
            "lng": lng,
        })

    facilities = [
        {
            "name": facility.name,
            "type": facility.facility_type,
            "type_label": facility.get_facility_type_display(),
            "address": facility.address,
            "phone": facility.phone,
            "lat": float(facility.latitude),
            "lng": float(facility.longitude),
        }
        for facility in Facility.objects.filter(is_active=True)
    ]

    return render(
        request,
        "locations/map.html",
        {
            "blood_type": blood_type,
            "blood_type_choices": User.BloodType.choices,
            "donor_count": len(donors),
            "map_data": {
                "center": map_center_for(request.user),
                "donors": donors,
                "facilities": facilities,
            },
        },
    )
