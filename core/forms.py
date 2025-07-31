from django import forms
from .models import PetProfile


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
