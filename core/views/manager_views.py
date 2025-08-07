from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from ..models import (
    UserProfile, PetProfile, Appointment, EmployeeCalendar
)
from ..forms import PetApprovalForm, AppointmentApprovalForm
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
    return render(request, 'core/manager_dashboard.html', {
        'pending_count': pending_count,
        'pending_appt_count': pending_appt_count,
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
                elif decision == 'reject':
                    pet.profile_status = 'rejected'

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
    pending_appointments = Appointment.objects.filter(status='pending')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        selected_appointment = get_object_or_404(
            Appointment, id=appointment_id
        )

        form = AppointmentApprovalForm(
            request.POST, prefix=str(appointment_id)
        )
        if form.is_valid():
            decision = form.cleaned_data['decision']
            selected_employee = form.cleaned_data['employee']

            if decision == 'approve':
                selected_appointment.employee = selected_employee
                selected_appointment.status = 'approved'
                selected_appointment.save()

                EmployeeCalendar.objects.create(
                    user_profile=selected_employee,
                    appointment=selected_appointment,
                    scheduled_time=selected_appointment.appointment_time,
                    available_time=False
                )

                success_msg = (f"Appointment approved and assigned to "
                               f"{selected_employee.user.username}.")
                messages.success(request, success_msg)
            elif decision == 'reject':
                selected_appointment.status = 'rejected'
                selected_appointment.save()
                messages.warning(request, "Appointment was rejected.")

            return redirect('approve_appointments')

    # Build forms with unique prefixes
    appointment_forms = []
    for appointment in pending_appointments:
        busy_employee_ids = EmployeeCalendar.objects.filter(
            scheduled_time=appointment.appointment_time
        ).values_list('user_profile_id', flat=True)

        available_employees = UserProfile.objects.filter(
            role='employee'
        ).exclude(id__in=busy_employee_ids)

        form = AppointmentApprovalForm(prefix=str(appointment.id))
        form.fields['employee'].queryset = available_employees
        appointment_forms.append((appointment, form))

    approved_appointments = Appointment.objects.filter(
        status='approved'
    ).order_by('appointment_time')

    return render(request, 'core/appointments_dashboard.html', {
        'appointment_forms': appointment_forms,
        'approved_appointments': approved_appointments,
    })
