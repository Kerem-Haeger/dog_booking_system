from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from datetime import date

from ..models import (
    UserProfile, PetProfile, Appointment, EmployeeCalendar, Service, ServicePrice
)
from ..forms import (
    PetApprovalForm, AppointmentApprovalForm, UserApprovalForm, 
    ServiceForm, ServicePriceForm, PetProfileManagerForm
)
from .roles import is_manager


@login_required
def manager_dashboard(request):
    """Dashboard view for managers showing pending counts"""
    pending_count = PetProfile.objects.filter(
        profile_status='pending'
    ).count()
    pending_appt_count = Appointment.objects.filter(
        status='pending'
    ).count()
    pending_user_count = UserProfile.objects.filter(
        role='pending'
    ).count()
    return render(request, 'core/manager_dashboard.html', {
        'pending_count': pending_count,
        'pending_appt_count': pending_appt_count,
        'pending_user_count': pending_user_count,
    })


@user_passes_test(is_manager)
def approve_pets(request):
    """Allow managers to approve or reject pending pet profiles and view all pets"""
    user_profile = getattr(request.user, 'userprofile', None)
    if (not request.user.is_authenticated or not user_profile or
            user_profile.role != 'manager'):
        return redirect('login')

    pending_pets = PetProfile.objects.filter(profile_status='pending')
    
    # Get all pets for the comprehensive view, with related data for efficiency
    all_pets = PetProfile.objects.select_related('user').prefetch_related(
        'appointment_set'
    ).exclude(profile_status='pending').order_by('-verified_at', 'name')
    
    # Calculate age for each pet
    for pet in all_pets:
        if pet.date_of_birth:
            today = date.today()
            birth_date = pet.date_of_birth
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            pet.calculated_age = age
        else:
            pet.calculated_age = None

    if request.method == 'POST':
        for pet in pending_pets:
            form = PetApprovalForm(request.POST, prefix=str(pet.id))
            if form.is_valid():
                decision = form.cleaned_data['decision']
                size = form.cleaned_data['size']

                if decision == 'approve':
                    pet.profile_status = 'verified'
                    pet.size = size
                    pet.verified_at = timezone.now()
                elif decision == 'reject':
                    pet.profile_status = 'rejected'

                pet.save()

        messages.success(request, "Pet profiles updated.")
        return redirect('approve_pets')

    pet_forms = [
        (pet, PetApprovalForm(prefix=str(pet.id)))
        for pet in pending_pets
    ]
    
    context = {
        'pet_forms': pet_forms,
        'all_pets': all_pets
    }
    return render(request, 'core/approve_pets.html', context)


@user_passes_test(is_manager)
def approve_appointments(request):
    """Allow managers to approve or reject pending appointments"""
    pending_appointments = Appointment.objects.filter(
        status='pending'
    ).order_by('appointment_time')  # Order by time - earliest first

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        # Get decision from button value
        decision = request.POST.get('decision')
        selected_appointment = get_object_or_404(
            Appointment, id=appointment_id
        )

        form = AppointmentApprovalForm(
            request.POST, prefix=str(appointment_id)
        )

        if decision == 'approve':
            if form.is_valid():
                selected_employee = form.cleaned_data['employee']
                if not selected_employee:
                    messages.error(
                        request, "Please select an employee for approval."
                    )
                    return redirect('approve_appointments')
                
                selected_appointment.employee = selected_employee
                selected_appointment.status = 'approved'
                selected_appointment.save()

                # Create EmployeeCalendar entry to mark employee as busy
                # First check if entry already exists to prevent duplicates
                existing_calendar = EmployeeCalendar.objects.filter(
                    user_profile=selected_employee,
                    scheduled_time=selected_appointment.appointment_time,
                    available_time=False
                ).first()
                
                if not existing_calendar:
                    EmployeeCalendar.objects.create(
                        user_profile=selected_employee,
                        appointment=selected_appointment,
                        scheduled_time=selected_appointment.appointment_time,
                        available_time=False
                    )

                success_msg = (f"Appointment approved and assigned to "
                               f"{selected_employee.user.username}. "
                               f"Page refreshed to update availability.")
                messages.success(request, success_msg)
            else:
                # Form has validation errors 
                messages.error(request, "Please correct the form errors.")
        elif decision == 'reject':
            selected_appointment.status = 'rejected'
            selected_appointment.save()
            
            messages.warning(request, "Appointment was rejected.")

        return redirect('approve_appointments')

    # Build forms with unique prefixes - dynamically filter available employees
    appointment_forms = []
    for appointment in pending_appointments:
        # Get all busy employees for appointments that overlap with this one
        from ..utils import get_overlapping_appointments
        
        # Get overlapping approved appointments
        overlapping_appointments = get_overlapping_appointments(appointment)
        busy_employee_ids_appointments = [appt.employee.id for appt in overlapping_appointments if appt.employee]
        
        # Also check EmployeeCalendar for this exact time (legacy support)
        busy_employee_ids_calendar = EmployeeCalendar.objects.filter(
            scheduled_time=appointment.appointment_time,
            available_time=False
        ).values_list('user_profile_id', flat=True)
        
        # Combine both sources to get all busy employees
        all_busy_employee_ids = list(busy_employee_ids_calendar) + busy_employee_ids_appointments
        
        available_employees = UserProfile.objects.filter(
            role='employee'
        ).exclude(id__in=all_busy_employee_ids)

        form = AppointmentApprovalForm(prefix=str(appointment.id))
        form.fields['employee'].queryset = available_employees
        
        # Add helpful info about availability
        form.fields['employee'].help_text = f"Available employees for {appointment.appointment_time.strftime('%Y-%m-%d %H:%M')}"
        
        appointment_forms.append((appointment, form))

    approved_appointments = Appointment.objects.filter(
        status='approved'
    ).order_by('appointment_time')

    # Get rejected appointments for separate display
    rejected_appointments = Appointment.objects.filter(
        status='rejected'
    ).order_by('-appointment_time')  # Most recent first

    # Get all employees for the filter dropdown
    all_employees = UserProfile.objects.filter(
        role='employee'
    ).select_related('user')

    return render(request, 'core/appointments_dashboard.html', {
        'appointment_forms': appointment_forms,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
        'all_employees': all_employees,
    })


@user_passes_test(is_manager)
def approve_users(request):
    """Allow managers to approve or reject pending users and manage all users"""
    # Get pending users
    pending_users = UserProfile.objects.filter(
        role='pending'
    ).select_related('user').order_by('created_at')
    
    # Get all users except the current manager for comprehensive management
    all_users = UserProfile.objects.exclude(
        user=request.user
    ).select_related('user').prefetch_related(
        'user__pets'
    ).order_by('role', 'user__username')

    if request.method == 'POST':
        # Check if it's a role update (comprehensive management)
        if 'role_update' in request.POST:
            # Handle role updates for all users
            for user_profile in all_users:
                role_field = f'role_{user_profile.id}'
                if role_field in request.POST:
                    new_role = request.POST.get(role_field)
                    valid_roles = [
                        choice[0] for choice in UserProfile.USER_ROLES
                    ]
                    
                    if (new_role in valid_roles and 
                            new_role != user_profile.role):
                        old_role = user_profile.role
                        user_profile.role = new_role
                        user_profile.save()
                        
                        messages.success(
                            request,
                            f'Updated {user_profile.user.username} role '
                            f'from {old_role} to {new_role}.'
                        )
            
            return redirect('approve_users')
        
        # Handle bulk actions for pending users
        elif 'bulk_approve_clients' in request.POST:
            for user_profile in pending_users:
                user_profile.role = 'client'
                user_profile.save()
            
            messages.success(
                request,
                f'Successfully approved {pending_users.count()} users.'
            )
            return redirect('approve_users')
        
        elif 'bulk_reject' in request.POST:
            count = pending_users.count()
            
            # Delete all pending users
            for user_profile in pending_users:
                user_profile.user.delete()
            
            messages.info(
                request,
                f'Rejected and deleted {count} pending user registrations.'
            )
            return redirect('approve_users')
        
        # Handle individual user actions for pending users
        else:
            for user_profile in pending_users:
                # Check for individual approve/reject buttons
                approve_key = f'user_{user_profile.id}_approve'
                reject_key = f'user_{user_profile.id}_reject'
                
                if approve_key in request.POST:
                    # Get the role from the form
                    role_field = f'id_{user_profile.id}-role'
                    role = request.POST.get(role_field, 'client')
                    
                    user_profile.role = role
                    user_profile.save()
                    
                    messages.success(
                        request,
                        f'User {user_profile.user.username} approved as {role}.'
                    )
                    return redirect('approve_users')
                
                elif reject_key in request.POST:
                    username = user_profile.user.username
                    
                    # Delete the user account
                    user_profile.user.delete()
                    
                    messages.info(
                        request,
                        f'Registration for {username} rejected and deleted.'
                    )
                    return redirect('approve_users')

    # Create forms for each pending user
    user_forms = []
    for user_profile in pending_users:
        form = UserApprovalForm(prefix=str(user_profile.id))
        user_forms.append((user_profile, form))
    
    # Group all users by role for better organization
    users_by_role = {}
    for user_profile in all_users:
        role = user_profile.role
        if role not in users_by_role:
            users_by_role[role] = []
        users_by_role[role].append(user_profile)

    context = {
        'user_forms': user_forms,
        'all_users': all_users,
        'users_by_role': users_by_role,
        'role_choices': UserProfile.USER_ROLES,
    }

    return render(request, 'core/approve_users.html', context)


@user_passes_test(is_manager)
def manage_services(request):
    """Service management dashboard for managers"""
    services = Service.objects.all().order_by('name')
    
    return render(request, 'core/manage_services.html', {
        'services': services,
    })


@user_passes_test(is_manager)
def create_service(request):
    """Create a new service"""
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            
            messages.success(
                request,
                f'Service "{service.name}" created successfully!'
            )
            return redirect('edit_service_pricing', service_id=service.id)
    else:
        form = ServiceForm()
    
    return render(request, 'core/create_service.html', {
        'form': form,
    })


@user_passes_test(is_manager)
def edit_service(request, service_id):
    """Edit an existing service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            
            messages.success(
                request,
                f'Service "{service.name}" updated successfully!'
            )
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'core/edit_service.html', {
        'form': form,
        'service': service,
    })


@user_passes_test(is_manager)
def edit_service_pricing(request, service_id):
    """Edit pricing for a service"""
    service = get_object_or_404(Service, id=service_id)
    
    # Get all existing prices for this service
    prices = ServicePrice.objects.filter(service=service)
    
    # Check if we're editing a specific price
    price_id = request.POST.get('price_id') or request.GET.get('price_id')
    price_instance = None
    if price_id:
        try:
            price_instance = ServicePrice.objects.get(id=price_id, service=service)
        except ServicePrice.DoesNotExist:
            pass
    
    if request.method == 'POST':
        if price_instance:
            # Editing existing price
            form = ServicePriceForm(request.POST, instance=price_instance)
        else:
            # Creating new price
            form = ServicePriceForm(request.POST)
        
        if form.is_valid():
            price_obj = form.save(commit=False)
            price_obj.service = service
            
            # Check if price already exists for this size
            existing_price = ServicePrice.objects.filter(
                service=service, 
                size=price_obj.size
            ).exclude(id=price_obj.id if price_obj.id else None).first()
            
            if existing_price:
                messages.error(
                    request,
                    f'Pricing for {price_obj.get_size_display()} size already exists. Use edit to update it.'
                )
            else:
                price_obj.save()
                
                action_text = 'updated' if price_instance else 'added'
                messages.success(
                    request,
                    f'Pricing for "{service.name}" ({price_obj.get_size_display()}) {action_text} successfully!'
                )
                return redirect('edit_service_pricing', service_id=service.id)
    else:
        if price_instance:
            form = ServicePriceForm(instance=price_instance)
        else:
            form = ServicePriceForm()
    
    return render(request, 'core/edit_service_pricing.html', {
        'service': service,
        'form': form,
        'prices': prices,
    })


@user_passes_test(is_manager)
def toggle_service_status(request, service_id):
    """Toggle active/inactive status of a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.is_active = not service.is_active
        service.save()
        
        status = "activated" if service.is_active else "deactivated"
        
        messages.success(
            request,
            f'Service "{service.name}" has been {status}!'
        )
    
    return redirect('manage_services')


@user_passes_test(is_manager)
def delete_service(request, service_id):
    """Allow manager to permanently delete a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service_name = service.name
        
        # Count related appointments
        related_appointments = Appointment.objects.filter(service=service)
        appointment_count = related_appointments.count()
        
        # Delete the service (this will cascade to related appointments and prices)
        service.delete()
        
        messages.success(
            request,
            f'Service "{service_name}" has been permanently deleted.'
        )
        return redirect('manage_services')
    
    # Get impact information for the confirmation page
    related_appointments = Appointment.objects.filter(service=service)
    appointment_count = related_appointments.count()
    active_appointments = related_appointments.exclude(status='canceled')
    
    context = {
        'service': service,
        'appointment_count': appointment_count,
        'active_appointments_count': active_appointments.count(),
        'service_prices': service.prices.all()
    }
    return render(request, 'core/delete_service.html', context)


@user_passes_test(is_manager)
def edit_pet(request, pet_id):
    """Allow manager to edit pet details"""
    pet = get_object_or_404(PetProfile, id=pet_id)
    
    if request.method == 'POST':
        form = PetProfileManagerForm(request.POST, instance=pet)
        if form.is_valid():
            updated_pet = form.save()
            
            messages.success(
                request,
                f'Pet "{updated_pet.name}" has been updated successfully.'
            )
            return redirect('approve_pets')
        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        form = PetProfileManagerForm(instance=pet)
    
    context = {
        'form': form,
        'pet': pet,
        'action': 'Edit'
    }
    return render(request, 'core/manager_edit_pet.html', context)


@user_passes_test(is_manager)
def delete_pet(request, pet_id):
    """Allow manager to delete a pet profile"""
    pet = get_object_or_404(PetProfile, id=pet_id)
    
    if request.method == 'POST':
        pet_name = pet.name
        
        pet.delete()
        
        messages.success(
            request,
            f'Pet "{pet_name}" has been permanently deleted.'
        )
        return redirect('approve_pets')
    
    context = {
        'pet': pet,
        'appointments_count': pet.appointment_set.count()
    }
    return render(request, 'core/manager_delete_pet.html', context)


@user_passes_test(is_manager)
def update_pet_status(request, pet_id):
    """Allow manager to update pet status"""
    pet = get_object_or_404(PetProfile, id=pet_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in PetProfile.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            old_status = pet.profile_status
            pet.profile_status = new_status
            
            # Update verification timestamp if status is being set to verified
            if new_status == 'verified' and old_status != 'verified':
                pet.verified_at = timezone.now()
            
            pet.save()
            
            messages.success(
                request,
                f'Pet "{pet.name}" status updated to {new_status}.'
            )
        else:
            messages.error(request, 'Invalid status provided.')
    
    return redirect('approve_pets')


@user_passes_test(is_manager)
def update_user_role(request, user_id):
    """Allow manager to update a single user's role"""
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        if new_role in [choice[0] for choice in UserProfile.USER_ROLES]:
            old_role = user_profile.role
            user_profile.role = new_role
            user_profile.save()
            
            user_display_name = (user_profile.user.get_full_name() or 
                                 user_profile.user.username)
            messages.success(
                request,
                f'Role for {user_display_name} updated from {old_role} to {new_role}.'
            )
        else:
            messages.error(request, 'Invalid role selected.')
    
    return redirect('approve_users')


@user_passes_test(is_manager)
def delete_user(request, user_id):
    """Allow manager to delete a user account"""
    user_profile = get_object_or_404(UserProfile, id=user_id)
    user = user_profile.user
    
    if request.method == 'POST':
        username = user.username
        full_name = user.get_full_name() or username
        
        # Check for related data
        pets_count = user.pets.count()
        appointments_count = sum(
            pet.appointment_set.count() for pet in user.pets.all()
        )
        
        # Delete user (cascades to UserProfile and related data)
        user.delete()
        
        messages.success(
            request,
            f'User "{full_name}" has been permanently deleted along with '
            f'{pets_count} pet(s) and {appointments_count} appointment(s).'
        )
        return redirect('approve_users')
    
    context = {
        'user_profile': user_profile,
        'pets_count': user.pets.count(),
        'appointments_count': sum(
            pet.appointment_set.count() for pet in user.pets.all()
        ),
    }
    return render(request, 'core/manager_delete_user.html', context)
