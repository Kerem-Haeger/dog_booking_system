from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import PetProfile, Appointment, ServicePrice
from ..forms import PetProfileForm, AppointmentForm


@login_required
def client_dashboard(request):
    """Dashboard view for clients showing their pets and appointments"""
    pets = PetProfile.objects.filter(user=request.user)
    
    # Get current datetime
    now = timezone.now()
    
    # Separate upcoming, past, and rejected appointments
    upcoming_appointments = Appointment.objects.filter(
        pet_profile__user=request.user,
        appointment_time__gte=now,
        status__in=['pending', 'approved']  # Exclude rejected from upcoming
    ).order_by('appointment_time')  # Nearest first
    
    past_appointments = Appointment.objects.filter(
        pet_profile__user=request.user,
        appointment_time__lt=now
    ).order_by('-appointment_time')  # Most recent first
    
    rejected_appointments = Appointment.objects.filter(
        pet_profile__user=request.user,
        status='rejected'
    ).order_by('-appointment_time')  # Most recent first

    # Add cancellation eligibility to upcoming appointments
    for appointment in upcoming_appointments:
        time_until_appointment = appointment.appointment_time - now
        appointment.can_cancel = (
            time_until_appointment.total_seconds() > 24 * 60 * 60 and
            appointment.status not in ['cancelled', 'rejected']
        )

    return render(request, 'core/client_dashboard_new.html', {
        'pets': pets,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'rejected_appointments': rejected_appointments,
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


@login_required
def cancel_appointment(request, appointment_id):
    """Allow clients to cancel appointments if more than 24 hours in advance"""
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        pet_profile__user=request.user
    )
    
    # Check if appointment is more than 24 hours in the future
    now = timezone.now()
    time_until_appointment = appointment.appointment_time - now
    
    # 24 hours in seconds
    if time_until_appointment.total_seconds() <= 24 * 60 * 60:
        messages.error(
            request,
            "Cannot cancel appointments within 24 hours. "
            "Please contact the business directly."
        )
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()
        
        formatted_time = appointment.appointment_time.strftime(
            "%H:%M on %d/%m/%Y"
        )
        messages.success(
            request,
            f"Appointment for {formatted_time} has been cancelled."
        )
        return redirect('client_dashboard')
    
    return render(request, 'core/cancel_appointment.html', {
        'appointment': appointment,
        'time_until_appointment': time_until_appointment
    })
