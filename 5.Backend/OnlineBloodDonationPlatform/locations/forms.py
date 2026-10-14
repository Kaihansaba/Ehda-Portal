from django import forms

from accounts.models import User

from .constants import AFGHANISTAN_BOUNDS, PROVINCE_CHOICES, PROVINCES, RADIUS_CHOICES
from .models import DonorLocation


def is_inside_afghanistan(latitude, longitude):
    return (
        AFGHANISTAN_BOUNDS["min_lat"] <= latitude <= AFGHANISTAN_BOUNDS["max_lat"]
        and AFGHANISTAN_BOUNDS["min_lng"] <= longitude <= AFGHANISTAN_BOUNDS["max_lng"]
    )


class DonorLocationForm(forms.ModelForm):
    """
    The donor clicks the map to fill latitude/longitude (hidden inputs).

    PRIVACY: the page never receives the stored exact point, so the hidden
    inputs start empty. If the donor only changes province/district and
    does not click the map again, the existing point is kept.
    """

    class Meta:
        model = DonorLocation
        fields = [
            "province",
            "district",
            "latitude",
            "longitude",
        ]
        widgets = {
            "province": forms.Select(),
            "district": forms.TextInput(
                attrs={"placeholder": "e.g. District 10"}
            ),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["latitude"].required = False
        self.fields["longitude"].required = False

        # Never send the stored exact point back to the browser.
        self.initial.pop("latitude", None)
        self.initial.pop("longitude", None)

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if latitude is None and longitude is None:
            if self.instance.pk:
                cleaned_data["latitude"] = self.instance.latitude
                cleaned_data["longitude"] = self.instance.longitude
                return cleaned_data

            raise forms.ValidationError(
                "Please click on the map to choose your location."
            )

        if latitude is None or longitude is None:
            raise forms.ValidationError(
                "Please click on the map to choose your location."
            )

        if not is_inside_afghanistan(float(latitude), float(longitude)):
            raise forms.ValidationError(
                "Please choose a location inside Afghanistan."
            )

        return cleaned_data


class DonorSearchForm(forms.Form):
    """Search filters. Submitted with GET so results can be bookmarked."""

    blood_type = forms.ChoiceField(
        choices=[("", "Select blood type")] + list(User.BloodType.choices),
    )

    include_compatible = forms.BooleanField(
        required=False,
        label="Include compatible donors",
        help_text="Also show donors whose blood type the patient can receive.",
    )

    province = forms.ChoiceField(
        choices=[("", "Any province")] + PROVINCE_CHOICES,
        required=False,
    )

    district = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Any district"}),
    )

    # Filled in by clicking the search map.
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    radius = forms.ChoiceField(
        choices=RADIUS_CHOICES,
        required=False,
        label="Distance",
    )

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if (latitude is None) != (longitude is None):
            raise forms.ValidationError(
                "Please click on the map again to choose a location."
            )

        if latitude is not None and not is_inside_afghanistan(latitude, longitude):
            raise forms.ValidationError(
                "Please choose a location inside Afghanistan."
            )

        if cleaned_data.get("radius") and self.origin_from(cleaned_data) is None:
            self.add_error(
                "radius",
                "Click on the map or choose a province to search within a distance.",
            )

        return cleaned_data

    @staticmethod
    def origin_from(cleaned_data):
        """The map point if one was clicked, else the province centre."""
        if cleaned_data.get("latitude") is not None:
            return (cleaned_data["latitude"], cleaned_data["longitude"])

        province = cleaned_data.get("province")
        if province:
            return PROVINCES[province]

        return None

    @property
    def origin(self):
        return self.origin_from(self.cleaned_data)

    @property
    def radius_km(self):
        radius = self.cleaned_data.get("radius")
        return int(radius) if radius else None
