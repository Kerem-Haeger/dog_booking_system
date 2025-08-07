from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import datetime

from ..models import PetProfile, Appointment, ServicePrice
from ..forms import PetProfileForm, AppointmentForm


@login_required
def client_dashboard(request):
    """Dashboard view for clients showing their pets and appointments"""
    pets = PetProfile.objects.filter(user=request.user)
    appointments = Appointment.objects.filter(
        pet_profile__user=request.user
    ).order_by('appointment_time')

    return render(request, 'core/client_dashboard.html', {
        'pets': pets,
        'appointments': appointments,
    })


@login_required
def add_pet(request):
    """Allow clients to add new pet profiles for approval"""
    if request.method == 'POST':
        form = PetProfileForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.user = request.user
            pet.profile_status = 'pending'  # default status
            pet.save()
            messages.success(request, "Pet profile submitted for approval!")
            return redirect('client_dashboard')
    else:
        form = PetProfileForm()

    return render(request, 'core/add_pet.html', {'form': form})


def book_appointment(request):
    """Allow clients to book appointments for their approved pets"""
    user_profile = getattr(request.user, 'userprofile', None)
    if not user_profile or user_profile.role != 'client':
        return redirect('login')

    if request.method == 'POST':
        print("Form submitted!")  # Debugging
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            print("Form is valid!")  # Debug
            appointment = form.save(commit=False)
            service = appointment.service
            # ISO string, e.g. "2025-08-12T14:00:00Z"
            time_slot_str = form.cleaned_data.get('time_slot')

            try:
                # Strip Z (if present from toISOString()) to avoid format error
                if time_slot_str.endswith("Z"):
                    time_slot_str = time_slot_str.rstrip("Z")

                # Parse and make timezone-aware
                combined_datetime = timezone.make_aware(
                    datetime.fromisoformat(time_slot_str)
                )
                appointment.appointment_time = combined_datetime
            except (ValueError, TypeError):
                messages.error(request, "Invalid time slot format.")
                return render(request, 'core/book_appointment.html',
                              {'form': form})

            try:
                pet_size = appointment.pet_profile.size
                appointment.final_price = service.get_price_for_size(pet_size)
            except ServicePrice.DoesNotExist:
                error_msg = (f"No price found for {service.name} "
                             f"and {pet_size} dogs.")
                messages.error(request, error_msg)
                return render(request, 'core/book_appointment.html',
                              {'form': form})
            
            appointment.status = 'pending'
            appointment.save()

            formatted = appointment.appointment_time.strftime(
                "%H:%M on %d/%m/%Y"
            )
            success_msg = (f"Appointment booked for {formatted} "
                           "and pending approval.")
            messages.success(request, success_msg)
            return redirect('client_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'core/book_appointment.html', {'form': form})
