"""
Dog Booking System
Author: Kerem Haeger
Created: August 2025
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
import bleach
from .models import (
    UserProfile,
    PetProfile,
    Appointment,
    Service,
    ServicePrice,
    )


class PetProfileForm(forms.ModelForm):
    """ Form for creating and editing pet profiles """
    class Meta:
        model = PetProfile
        fields = ['name', 'breed', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Sanitize pet name - allow only basic characters
            sanitized = bleach.clean(name, tags=[], strip=True)
            if not sanitized or len(sanitized.strip()) < 2:
                raise forms.ValidationError(
                    "Pet name must be at least 2 characters long."
                )
            return sanitized.strip()
        return name

    def clean_breed(self):
        breed = self.cleaned_data.get('breed')
        if breed:
            # Sanitize breed - allow only basic characters
            sanitized = bleach.clean(breed, tags=[], strip=True)
            if not sanitized or len(sanitized.strip()) < 2:
                raise forms.ValidationError(
                    "Breed must be at least 2 characters long."
                )
            return sanitized.strip()
        return breed

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = timezone.now().date()

            # Check if birth date is in the future
            if date_of_birth > today:
                raise forms.ValidationError(
                    "Birth date cannot be in the future."
                )

            # Optional: Check if birth date is too far in the past
            # (e.g., older than 30 years)
            max_age_years = 30
            min_birth_date = today.replace(year=today.year - max_age_years)
            if date_of_birth < min_birth_date:
                raise forms.ValidationError(
                    f"Birth date cannot be more than {max_age_years} "
                    f"years ago."
                )

        return date_of_birth


class PetProfileManagerForm(forms.ModelForm):
    """ Manager/Employee form for editing pet profiles including grooming preferences """
    class Meta:
        model = PetProfile
        fields = [
            'name',
            'breed',
            'date_of_birth',
            'grooming_preferences',
            'size',
            'profile_status'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'grooming_preferences': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_grooming_preferences(self):
        preferences = self.cleaned_data.get('grooming_preferences')
        if preferences:
            # Sanitize preferences - allow basic formatting
            allowed_tags = []  # No HTML tags allowed
            sanitized = bleach.clean(
                preferences, tags=allowed_tags, strip=True
            )
            return sanitized.strip()
        return preferences


class PetApprovalForm(forms.Form):
    """ Form for approving or rejecting pet profiles """
    size = forms.ChoiceField(
        choices=[('', '--- Select Size ---')] + PetProfile.SIZE_CHOICES,
        required=True,  # Changed to True for proper validation
        label="Assign Size (for approval)"
    )
    decision = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.HiddenInput(),
        required=True
    )


class AppointmentForm(forms.ModelForm):
    """ Form for creating and editing appointments """
    voucher_code = forms.CharField(
        max_length=20, required=False,
        label="Voucher Code (Optional)"
    )

    time_slot = forms.CharField(
        required=True,
        label="Choose a Time Slot",
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Appointment
        fields = ['pet_profile', 'service']
        widgets = {
            'appointment_time': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Filter to show only verified pets owned by this user
        self.fields['pet_profile'].queryset = PetProfile.objects.filter(
            user=user, profile_status='verified'
        )

        # Filter to show only active services
        self.fields['service'].queryset = Service.objects.filter(
            is_active=True
        ).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        pet_profile = cleaned_data.get('pet_profile')
        time_slot = cleaned_data.get('time_slot')

        if pet_profile and time_slot:
            try:
                # Parse the time slot to get the date
                if time_slot.endswith("Z"):
                    time_slot = time_slot.rstrip("Z")

                combined_datetime = timezone.make_aware(
                    datetime.fromisoformat(time_slot)
                )

                # Check if appointment is in the future
                if combined_datetime <= timezone.now():
                    raise forms.ValidationError(
                        "Appointments can only be booked for future dates and times."
                    )

                # Check daily appointment limit (max 2 per day)
                same_day_count = Appointment.objects.filter(
                    pet_profile__user=pet_profile.user,
                    appointment_time__date=combined_datetime.date(),
                    status__in=['pending', 'approved']
                ).count()

                if same_day_count >= 2:
                    raise forms.ValidationError(
                        "Maximum 2 appointments allowed per day."
                    )

            except (ValueError, TypeError):
                pass  # Let time_slot validation handle the error

        return cleaned_data

    def clean_appointment_time(self):
        appt_datetime = self.cleaned_data['appointment_time']
        now = timezone.now()

        # Must be in the future
        if appt_datetime.date() < now.date():
            raise forms.ValidationError(
                "Appointment date must be in the future."
            )

        # Business hours validation (9 AM - 6 PM)
        if appt_datetime.hour < 9 or appt_datetime.hour >= 18:
            raise forms.ValidationError(
                "Appointments are only available between 9 AM and 6 PM."
            )

        # No appointments on Sundays (weekday 6)
        if appt_datetime.weekday() == 6:
            raise forms.ValidationError(
                "Appointments are not available on Sundays."
            )

        # Maximum advance booking (3 months)
        max_advance = now + timedelta(days=90)
        if appt_datetime > max_advance:
            raise forms.ValidationError(
                "Cannot book more than 3 months in advance."
            )

        return appt_datetime


class AppointmentApprovalForm(forms.Form):
    """ Form for approving or rejecting appointments """
    employee = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(role='employee'),
        label="Assign to Employee",
        required=False,  # Not required - only needed for approval
        empty_label="Select an employee..."
    )


class UserApprovalForm(forms.Form):
    """Form for approving pending user registrations"""
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='client',
        label="Assign Role"
    )


class ServiceForm(forms.ModelForm):
    """ Form for creating and editing services """

    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'allowed_start_times', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'allowed_start_times': forms.TextInput(attrs={
                'placeholder': 'e.g., 09:00,11:30,14:00',
                'help_text': 'Comma-separated start times'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Sanitize service name
            sanitized = bleach.clean(name, tags=[], strip=True)
            if not sanitized or len(sanitized.strip()) < 2:
                raise forms.ValidationError(
                    "Service name must be at least 2 characters long."
                )
            return sanitized.strip()
        return name

    def clean_allowed_start_times(self):
        times_str = self.cleaned_data.get('allowed_start_times')
        if not times_str or not times_str.strip():
            raise forms.ValidationError(
                "Please specify at least one allowed start time."
            )

        # Validate time format
        times = [t.strip() for t in times_str.split(',')]
        for time_str in times:
            try:
                # Try to parse as HH:MM format
                datetime.strptime(time_str, '%H:%M')
            except ValueError:
                raise forms.ValidationError(
                    f"Invalid time format: '{time_str}'. Use HH:MM format (e.g., 09:00)."
                )

        return times_str

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration:
            # Convert to total seconds for validation
            total_seconds = duration.total_seconds()

            # Minimum 15 minutes
            if total_seconds < 15 * 60:
                raise forms.ValidationError(
                    "Service duration must be at least 15 minutes."
                )

            # Maximum 8 hours
            if total_seconds > 8 * 60 * 60:
                raise forms.ValidationError(
                    "Service duration cannot exceed 8 hours."
                )

        return duration


class ServicePriceForm(forms.ModelForm):
    """ Form for managing service pricing """

    class Meta:
        model = ServicePrice
        fields = ['size', 'price']
        widgets = {
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None:
            if price <= 0:
                raise forms.ValidationError(
                    "Price must be greater than 0."
                )
            if price > 999.99:
                raise forms.ValidationError(
                    "Price cannot exceed $999.99."
                )
        return price


class CustomUserRegistrationForm(UserCreationForm):
    """ Extended registration form with additional user information """

    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Enter your first name"
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Enter your last name"
    )

    email = forms.EmailField(
        required=False,
        help_text="Optional: Enter your email address"
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize username field
        self.fields['username'].max_length = 20
        self.fields['username'].help_text = (
            "Required. 20 characters or fewer. "
            "Letters, digits, and special characters allowed."
        )

    def clean_username(self):
        """Validate username length and uniqueness"""
        username = self.cleaned_data.get('username')

        if len(username) > 20:
            raise ValidationError("Username cannot be longer than 20 characters.")

        # Check if username already exists (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with this username already exists.")

        return username

    def clean_email(self):
        """Validate email if provided"""
        email = self.cleaned_data.get('email')

        if email:
            # Check if email already exists (case-insensitive)
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError("A user with this email already exists.")

        return email
