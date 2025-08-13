from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from django_ratelimit.decorators import ratelimit

from ..models import PetProfile, Appointment, ServicePrice
from ..forms import PetProfileForm, AppointmentForm
from ..utils import log_audit_action


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

    # The can_cancel and can_edit properties are already defined in the model

    return render(request, 'core/client_dashboard.html', {
        'pets': pets,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'rejected_appointments': rejected_appointments,
    })


@login_required
@ratelimit(key='user', rate='3/h', method='POST', block=True)
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


@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=True)
def edit_pet(request, pet_id):
    """Allow clients to edit their pet profiles"""
    pet = get_object_or_404(PetProfile, id=pet_id, user=request.user)

    if request.method == 'POST':
        form = PetProfileForm(request.POST, instance=pet)
        if form.is_valid():
            updated_pet = form.save(commit=False)

            # If pet was verified and we're making changes to core info,
            # reset to pending
            if pet.profile_status == 'verified':
                original_pet = PetProfile.objects.get(id=pet.id)
                if (original_pet.name != updated_pet.name or
                        original_pet.breed != updated_pet.breed or
                        original_pet.date_of_birth !=
                        updated_pet.date_of_birth):
                    updated_pet.profile_status = 'pending'
                    updated_pet.size = None  # Reset size assignment
                    messages.warning(
                        request,
                        "Changes to pet information require re-approval. "
                        "Your pet profile has been resubmitted for review."
                    )
                else:
                    messages.success(
                        request,
                        "Pet profile updated successfully!"
                    )
            # Reset status to pending if it was rejected and is being updated
            elif pet.profile_status == 'rejected':
                updated_pet.profile_status = 'pending'
                messages.success(
                    request,
                    "Pet profile updated and resubmitted for approval!"
                )
            else:
                messages.success(request, "Pet profile updated!")

            updated_pet.save()
            return redirect('client_dashboard')
    else:
        form = PetProfileForm(instance=pet)

    return render(request, 'core/edit_pet.html', {
        'form': form,
        'pet': pet
    })


@login_required
@ratelimit(key='user', rate='3/h', method='POST', block=True)
def delete_pet(request, pet_id):
    """Allow clients to delete their pet profiles, canceling future appointments"""
    pet = get_object_or_404(PetProfile, id=pet_id, user=request.user)
    
    # Check for future appointments that will be cancelled
    from django.utils import timezone
    future_appointments = Appointment.objects.filter(
        pet_profile=pet,
        appointment_time__gt=timezone.now(),
        status__in=['pending', 'approved']
    )
    
    if request.method == 'POST':
        pet_name = pet.name
        future_count = future_appointments.count()
        
        # Cancel all future appointments for this pet
        if future_count > 0:
            future_appointments.update(status='canceled')
            messages.warning(
                request,
                f"Cancelled {future_count} future appointment(s) for {pet_name}."
            )
        
        # Delete the pet profile
        pet.delete()
        messages.success(
            request,
            f"Pet profile for {pet_name} has been removed from your account."
        )
        return redirect('client_dashboard')
    
    return render(request, 'core/delete_pet.html', {
        'pet': pet,
        'future_appointments': future_appointments
    })


@ratelimit(key='user', rate='5/h', method='POST', block=True)
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
                
                # Additional security check: ensure appointment is in the future
                if combined_datetime <= timezone.now():
                    messages.error(
                        request, 
                        "Appointments can only be booked for future dates and times."
                    )
                    return render(request, 'core/book_appointment.html',
                                  {'form': form})
                
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
        
        # Log audit action
        log_audit_action(
            user=request.user,
            action='appointment_cancelled',
            details={
                'appointment_id': appointment.id,
                'pet_name': appointment.pet_profile.name,
                'service': appointment.service.name,
                'appointment_time': appointment.appointment_time.isoformat(),
                'hours_before': time_until_appointment.total_seconds() / 3600
            },
            request=request
        )
        
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


@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=True)
def edit_appointment(request, appointment_id):
    """Allow clients to edit appointments if more than 24h away and under 3 edits"""
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        pet_profile__user=request.user
    )
    
    # Check if appointment is more than 24 hours in the future
    now = timezone.now()
    time_until_appointment = appointment.appointment_time - now
    
    if time_until_appointment.total_seconds() <= 24 * 60 * 60:
        messages.error(
            request,
            "Cannot edit appointments within 24 hours. "
            "Please contact the business directly."
        )
        return redirect('client_dashboard')
    
    # Check edit count limit
    if appointment.edit_count >= 3:
        messages.error(
            request,
            "You have reached the maximum number of edits (3) for this "
            "appointment. Please contact the business directly for further "
            "changes."
        )
        return redirect('client_dashboard')
    
    # Check if appointment can be edited
    if appointment.status in ['cancelled', 'completed']:
        messages.error(
            request,
            "Cannot edit cancelled or completed appointments."
        )
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user, instance=appointment)
        if form.is_valid():
            # Store original values for comparison
            original_time = appointment.appointment_time
            original_service = appointment.service
            
            updated_appointment = form.save(commit=False)
            
            # Ensure pet profile doesn't change (security measure)
            updated_appointment.pet_profile = appointment.pet_profile
            
            service = updated_appointment.service
            time_slot_str = form.cleaned_data.get('time_slot')

            try:
                # Parse time slot
                if time_slot_str.endswith("Z"):
                    time_slot_str = time_slot_str.rstrip("Z")

                # Parse the datetime string
                parsed_datetime = datetime.fromisoformat(time_slot_str)
                
                # Check if it's naive or aware
                if timezone.is_naive(parsed_datetime):
                    combined_datetime = timezone.make_aware(parsed_datetime)
                else:
                    combined_datetime = parsed_datetime
                
                # Security check: ensure appointment is in the future
                if combined_datetime <= timezone.now():
                    messages.error(
                        request, 
                        "Appointments can only be scheduled for future times."
                    )
                    return render(request, 'core/edit_appointment.html', {
                        'form': form, 'appointment': appointment,
                        'edits_remaining': 3 - appointment.edit_count,
                        'time_until_appointment': time_until_appointment
                    })
                
                updated_appointment.appointment_time = combined_datetime
            except (ValueError, TypeError):
                messages.error(request, "Invalid time slot format.")
                return render(request, 'core/edit_appointment.html', {
                    'form': form, 'appointment': appointment,
                    'edits_remaining': 3 - appointment.edit_count,
                    'time_until_appointment': time_until_appointment
                })

            # Calculate new price
            try:
                pet_size = updated_appointment.pet_profile.size
                updated_appointment.final_price = service.get_price_for_size(pet_size)
            except ServicePrice.DoesNotExist:
                messages.error(
                    request, 
                    f"No price found for {service.name} and {pet_size} dogs."
                )
                return render(request, 'core/edit_appointment.html', {
                    'form': form, 'appointment': appointment,
                    'edits_remaining': 3 - appointment.edit_count,
                    'time_until_appointment': time_until_appointment
                })

            # Reset to pending and increment edit count
            updated_appointment.status = 'pending'
            updated_appointment.edit_count += 1
            updated_appointment.save()

            # Log audit action
            log_audit_action(
                user=request.user,
                action='appointment_edited',
                details={
                    'appointment_id': appointment.id,
                    'pet_name': appointment.pet_profile.name,
                    'original_service': original_service.name,
                    'new_service': service.name,
                    'original_time': original_time.isoformat(),
                    'new_time': combined_datetime.isoformat(),
                    'edit_count': updated_appointment.edit_count,
                    'hours_before': time_until_appointment.total_seconds() / 3600
                },
                request=request
            )

            formatted_time = updated_appointment.appointment_time.strftime(
                "%H:%M on %d/%m/%Y"
            )
            
            edits_remaining = 3 - updated_appointment.edit_count
            if edits_remaining > 0:
                messages.success(
                    request,
                    f"Appointment updated for {formatted_time} and pending "
                    f"approval. You have {edits_remaining} edit(s) remaining."
                )
            else:
                messages.success(
                    request,
                    f"Appointment updated for {formatted_time} and pending "
                    "approval. No more edits allowed - contact us for further "
                    "changes."
                )
            
            return redirect('client_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-populate form with current appointment data
        form = AppointmentForm(user=request.user, instance=appointment)

    edits_remaining = 3 - appointment.edit_count
    return render(request, 'core/edit_appointment.html', {
        'form': form,
        'appointment': appointment,
        'edits_remaining': edits_remaining,
        'time_until_appointment': time_until_appointment
    })
