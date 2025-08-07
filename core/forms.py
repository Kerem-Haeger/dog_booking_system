from django import forms
from django.utils import timezone
from datetime import timedelta, datetime
import bleach
from .models import (
    User,
    UserProfile,
    PetProfile,
    Appointment,
    Service,
    Voucher
    )


class PetProfileForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ['name', 'breed', 'date_of_birth', 'grooming_preferences']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'grooming_preferences': forms.Textarea(attrs={'rows': 3}),
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

        # Filter to show only approved pets owned by this user
        self.fields['pet_profile'].queryset = PetProfile.objects.filter(
            user=user, profile_status='approved'
        )

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
    employee = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(role='employee'),
        label="Assign to Employee"
    )
