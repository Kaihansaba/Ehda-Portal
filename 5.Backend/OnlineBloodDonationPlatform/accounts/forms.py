from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from locations.utils import compatible_donor_types, public_name

from .models import User, BloodRequest, Donation, Report


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
        validators=[validate_password],
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm your password"}
        ),
    )

    role = forms.ChoiceField(
        choices=[
            (User.Role.DONOR, "Donor"),
            (User.Role.HOSPITAL, "Hospital"),
        ],
        widget=forms.Select(),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "blood_type",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "First name"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Last name"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email address"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Phone number"}
            ),
            "blood_type": forms.Select(),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()

        existing_users = User.objects.filter(
            email=email
        ).exclude(pk=self.instance.pk)

        if existing_users.exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ["blood_type", "units_needed", "urgency", "notes"]
        widgets = {
            "blood_type": forms.Select(attrs={"class": "form-control"}),
            "units_needed": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "urgency": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, target_donor=None, **kwargs):
        super().__init__(*args, **kwargs)
        # A donor chosen in search (#010); the request is sent to them only.
        self.target_donor = target_donor

    def clean_blood_type(self):
        blood_type = self.cleaned_data.get("blood_type")
        donor = self.target_donor

        if donor and blood_type and donor.blood_type not in compatible_donor_types(blood_type):
            raise forms.ValidationError(
                f"{public_name(donor)} has blood type {donor.blood_type}, which can't be "
                f"given to a patient who needs {blood_type}."
            )
        return blood_type

    def clean_units_needed(self):
        units = self.cleaned_data.get("units_needed")
        if units is not None and units <= 0:
            raise forms.ValidationError("Units needed must be greater than 0.")
        return units

    # The "notes required for urgent/emergency" rule lives in
    # BloodRequest.clean(), which ModelForm runs automatically. Checking it
    # here as well showed the same error twice.


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.RadioSelect(),
            "details": forms.Textarea(attrs={"rows": 5, "maxlength": 2000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No pre-selected blank "Select an option" radio button.
        self.fields["reason"].choices = Report.Reason.choices

    def clean_details(self):
        details = self.cleaned_data["details"].strip()
        if len(details) < 10:
            raise forms.ValidationError("Please describe what happened (at least 10 characters).")
        return details


class DonationForm(forms.ModelForm):
    """A donor's own donation record (#015). Blood type comes from the profile."""

    class Meta:
        model = Donation
        fields = ["donation_date", "place", "notes"]
        widgets = {
            "donation_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "place": forms.TextInput(attrs={"placeholder": "e.g. Kabul Blood Bank", "maxlength": 200}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["donation_date"].widget.attrs["max"] = today.isoformat()

    def clean_donation_date(self):
        donation_date = self.cleaned_data["donation_date"]
        if donation_date > timezone.localdate():
            raise forms.ValidationError("The donation date can't be in the future.")
        return donation_date
