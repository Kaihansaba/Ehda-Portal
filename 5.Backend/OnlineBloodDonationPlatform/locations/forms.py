from django import forms

from .constants import AFGHANISTAN_BOUNDS
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
