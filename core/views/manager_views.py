from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from ..models import (
    UserProfile, PetProfile, Appointment, EmployeeCalendar, Service, ServicePrice
)
from ..forms import (
    PetApprovalForm, AppointmentApprovalForm, UserApprovalForm, 
    ServiceForm, ServicePriceForm
)
from ..utils import log_audit_action
from .base import is_manager


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
    """Allow managers to approve or reject pending pet profiles"""
    user_profile = getattr(request.user, 'userprofile', None)
    if (not request.user.is_authenticated or not user_profile or
            user_profile.role != 'manager'):
        return redirect('login')

    pending_pets = PetProfile.objects.filter(profile_status='pending')

    if request.method == 'POST':
        for pet in pending_pets:
            form = PetApprovalForm(request.POST, prefix=str(pet.id))
            if form.is_valid():
                decision = form.cleaned_data['decision']
                size = form.cleaned_data['size']

                if decision == 'approve':
                    pet.profile_status = 'approved'
                    pet.size = size
                    pet.verified_at = timezone.now()
                    
                    # Log audit action
                    log_audit_action(
                        user=request.user,
                        action='pet_approved',
                        target_user=pet.user,
                        details={
                            'pet_id': pet.id,
                            'pet_name': pet.name,
                            'assigned_size': size
                        },
                        request=request
                    )
                elif decision == 'reject':
                    pet.profile_status = 'rejected'
                    
                    # Log audit action
                    log_audit_action(
                        user=request.user,
                        action='pet_rejected',
                        target_user=pet.user,
                        details={
                            'pet_id': pet.id,
                            'pet_name': pet.name
                        },
                        request=request
                    )

                pet.save()

        messages.success(request, "Pet profiles updated.")
        return redirect('approve_pets')

    pet_forms = [
        (pet, PetApprovalForm(prefix=str(pet.id)))
        for pet in pending_pets
    ]
    return render(request, 'core/approve_pets.html', {'pet_forms': pet_forms})


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

                # Log audit action
                log_audit_action(
                    user=request.user,
                    action='appointment_approved',
                    target_user=selected_appointment.pet_profile.user,
                    details={
                        'appointment_id': selected_appointment.id,
                        'pet_name': selected_appointment.pet_profile.name,
                        'service': selected_appointment.service.name,
                        'employee': selected_employee.user.username,
                        'appointment_time':
                            selected_appointment.appointment_time.isoformat()
                    },
                    request=request
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
            
            # Log audit action
            log_audit_action(
                user=request.user,
                action='appointment_rejected',
                target_user=selected_appointment.pet_profile.user,
                details={
                    'appointment_id': selected_appointment.id,
                    'pet_name': selected_appointment.pet_profile.name,
                    'service': selected_appointment.service.name,
                    'appointment_time':
                        selected_appointment.appointment_time.isoformat()
                },
                request=request
            )
            
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
    """Allow managers to approve or reject pending user registrations"""
    pending_users = UserProfile.objects.filter(
        role='pending'
    ).select_related('user').order_by('created_at')

    if request.method == 'POST':
        for user_profile in pending_users:
            form = UserApprovalForm(request.POST, prefix=str(user_profile.id))
            if form.is_valid():
                decision = form.cleaned_data['decision']
                role = form.cleaned_data['role']

                if decision == 'approve':
                    user_profile.role = role
                    user_profile.save()
                    
                    # Log audit action
                    log_audit_action(
                        user=request.user,
                        action='user_approved',
                        details={
                            'approved_user': user_profile.user.username,
                            'assigned_role': role
                        },
                        target_user=user_profile.user,
                        request=request
                    )
                    
                    messages.success(
                        request,
                        f'User {user_profile.user.username} approved as {role}.'
                    )
                elif decision == 'reject':
                    username = user_profile.user.username
                    
                    # Log audit action before deletion
                    log_audit_action(
                        user=request.user,
                        action='user_rejected',
                        details={
                            'rejected_user': username,
                            'reason': 'Registration rejected by manager'
                        },
                        target_user=user_profile.user,
                        request=request
                    )
                    
                    # Delete the entire user account
                    user_profile.user.delete()  # This also deletes UserProfile due to cascade
                    
                    messages.info(
                        request,
                        f'User registration for {username} has been rejected and deleted.'
                    )

        return redirect('approve_users')

    # Create forms for each pending user
    user_forms = []
    for user_profile in pending_users:
        form = UserApprovalForm(prefix=str(user_profile.id))
        user_forms.append((user_profile, form))

    return render(request, 'core/approve_users.html', {
        'user_forms': user_forms,
    })


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
            
            # Log audit action
            log_audit_action(
                user=request.user,
                action='service_created',
                details={
                    'service_name': service.name,
                    'duration': str(service.duration),
                    'allowed_times': service.allowed_start_times
                },
                request=request
            )
            
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
            old_name = service.name
            service = form.save()
            
            # Log audit action
            log_audit_action(
                user=request.user,
                action='service_updated',
                details={
                    'service_name': service.name,
                    'old_name': old_name if old_name != service.name else None,
                    'duration': str(service.duration),
                    'is_active': service.is_active
                },
                request=request
            )
            
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
                
                # Log audit action
                action = 'service_pricing_updated' if price_instance else 'service_pricing_added'
                log_audit_action(
                    user=request.user,
                    action=action,
                    details={
                        'service_name': service.name,
                        'size': price_obj.get_size_display(),
                        'price': str(price_obj.price)
                    },
                    request=request
                )
                
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
        
        # Log audit action
        log_audit_action(
            user=request.user,
            action='service_status_changed',
            details={
                'service_name': service.name,
                'new_status': 'active' if service.is_active else 'inactive'
            },
            request=request
        )
        
        messages.success(
            request,
            f'Service "{service.name}" has been {status}!'
        )
    
    return redirect('manage_services')
