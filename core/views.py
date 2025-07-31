from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from .models import (
    User,
    UserProfile,
    PetProfile,
    Appointment,
    Voucher,
    Service,
    EmployeeCalendar,
    )
from .forms import (
    PetProfileForm,
    PetApprovalForm,
    AppointmentForm,
    AppointmentApprovalForm,
    )


@login_required
def redirect_by_role(request):
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')

    try:
        role = user.userprofile.role
    except UserProfile.DoesNotExist:
        return HttpResponse(
            "Error: This user does not have a UserProfile."
            "Please create one via the admin site."
            )

    if role == 'client':
        return redirect('client_dashboard')
    elif role == 'employee':
        return redirect('employee_dashboard')
    elif role == 'manager':
        return redirect('manager_dashboard')
    else:
        return HttpResponse("Unknown role.")


@login_required
def client_dashboard(request):
    pets = PetProfile.objects.filter(user=request.user)
    return render(request, 'core/client_dashboard.html', {
        'pets': pets
    })


@login_required
def employee_dashboard(request):
    return render(request, 'core/employee_dashboard.html')


@login_required
def manager_dashboard(request):
    pending_count = PetProfile.objects.filter(profile_status='pending').count()
    return render(request, 'core/manager_dashboard.html', {
        'pending_count': pending_count
    })


def is_manager(user):
    return (
        user.is_authenticated and
        hasattr(user, 'userprofile') and
        user.userprofile.role == 'manager'
    )


@user_passes_test(is_manager)
def approve_pets(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'manager':
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

    pet_forms = [(pet, PetApprovalForm(prefix=str(pet.id))) for pet in pending_pets]
    return render(request, 'core/approve_pets.html', {'pet_forms': pet_forms})


@login_required
def add_pet(request):
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
def book_appointment(request):
    # Only clients should access this
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'client':
        return redirect('login')

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            service = appointment.service
            voucher_code = form.cleaned_data.get('voucher_code')
            final_price = service.price
            voucher = None

            if voucher_code:
                try:
                    voucher = Voucher.objects.get(code=voucher_code, is_redeemed=False)
                    if voucher.expiry_date < timezone.now().date():
                        messages.error(request, "Voucher has expired.")
                    else:
                        final_price = service.price * (1 - voucher.discount_percentage / 100)
                        appointment.voucher = voucher
                except Voucher.DoesNotExist:
                    messages.error(request, "Invalid voucher code.")

            appointment.final_price = round(final_price, 2)
            appointment.status = 'pending'
            appointment.save()

            if voucher:
                voucher.is_redeemed = True
                voucher.used_by_user = request.user
                voucher.save()

            messages.success(request, "Appointment booked and pending approval.")
            return redirect('client_dashboard')
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'core/book_appointment.html', {'form': form})


@user_passes_test(is_manager)
def approve_appointments(request):
    pending_appointments = Appointment.objects.filter(status='pending')

    if request.method == 'POST':
        form = AppointmentApprovalForm(request.POST)
        if form.is_valid():
            appointment_id = request.POST.get('appointment_id')
            decision = form.cleaned_data['decision']
            selected_employee = form.cleaned_data['employee']

            appointment = Appointment.objects.get(id=appointment_id)

            if decision == 'approve':
                appointment.employee = selected_employee
                appointment.status = 'approved'
                appointment.save()

                # Add to employee calendar
                EmployeeCalendar.objects.create(
                    user_profile=selected_employee,
                    appointment=appointment,
                    scheduled_time=appointment.appointment_time,
                    available_time=False  # now marked as unavailable
                )

            elif decision == 'reject':
                appointment.status = 'rejected'
                appointment.save()

            return redirect('approve_appointments')

    # Build form for each appointment with available employees
    appointment_forms = []
    for appointment in pending_appointments:
        # Employees already scheduled at this time
        busy_employee_ids = EmployeeCalendar.objects.filter(
            scheduled_time=appointment.appointment_time
        ).values_list('user_profile_id', flat=True)

        # Only employees not scheduled at that time
        available_employees = UserProfile.objects.filter(
            role='employee'
        ).exclude(id__in=busy_employee_ids)

        form = AppointmentApprovalForm()
        form.fields['employee'].queryset = available_employees
        appointment_forms.append((appointment, form))

    return render(request, 'core/approve_appointments.html', {
        'appointment_forms': appointment_forms
    })
