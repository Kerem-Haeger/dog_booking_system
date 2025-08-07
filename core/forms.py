from django import forms
from django.utils import timezone
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
        widget=forms.HiddenInput()  # we hide it from rendering; your custom <select> handles it
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

    def clean_appointment_time(self):
        appt_datetime = self.cleaned_data['appointment_time']
        if appt_datetime.date() < timezone.now().date():
            raise forms.ValidationError("Appointment date must be in the future.")
        return appt_datetime


class AppointmentApprovalForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(role='employee'),
        label="Assign to Employee"
    )
