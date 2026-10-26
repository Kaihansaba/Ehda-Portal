from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User, BloodRequest


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

    def clean_units_needed(self):
        units = self.cleaned_data.get("units_needed")
        if units is not None and units <= 0:
            raise forms.ValidationError("Units needed must be greater than 0.")
        return units

    # The "notes required for urgent/emergency" rule lives in
    # BloodRequest.clean(), which ModelForm runs automatically. Checking it
    # here as well showed the same error twice.