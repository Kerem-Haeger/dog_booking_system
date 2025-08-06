from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET
from datetime import datetime, timedelta
from .models import (
    User,
    UserProfile,
    PetProfile,
    Appointment,
    Voucher,
    Service,
    ServicePrice,
    EmployeeCalendar,
    )
from .forms import (
    PetProfileForm,
    PetApprovalForm,
    AppointmentForm,
    AppointmentApprovalForm,
    )
from .utils import get_available_slots


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
    appointments = Appointment.objects.filter(
        pet_profile__user=request.user
    ).order_by('appointment_time')

    return render(request, 'core/client_dashboard.html', {
        'pets': pets,
        'appointments': appointments,
    })


@login_required
def employee_dashboard(request):
    return render(request, 'core/employee_dashboard.html')


@login_required
def manager_dashboard(request):
    pending_count = PetProfile.objects.filter(profile_status='pending').count()
    pending_appt_count = Appointment.objects.filter(status='pending').count()
    return render(request, 'core/manager_dashboard.html', {
        'pending_count': pending_count,
        'pending_appt_count': pending_appt_count,
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
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'client':
        return redirect('login')

    if request.method == 'POST':
        print("Form submitted!")  # Debugging
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            print("Form is valid!")  # Debug
            appointment = form.save(commit=False)
            service = appointment.service
            time_slot_str = form.cleaned_data.get('time_slot')  # ISO string, e.g. "2025-08-12T14:00:00Z"

            try:
                # Strip Z (if present from toISOString()) to avoid format error
                if time_slot_str.endswith("Z"):
                    time_slot_str = time_slot_str.rstrip("Z")

                # Parse and make timezone-aware
                combined_datetime = timezone.make_aware(datetime.fromisoformat(time_slot_str))
                appointment.appointment_time = combined_datetime
            except (ValueError, TypeError):
                messages.error(request, "Invalid time slot format.")
                return render(request, 'core/book_appointment.html', {'form': form})

            try:
                pet_size = appointment.pet_profile.size
                appointment.final_price = service.get_price_for_size(pet_size)
            except ServicePrice.DoesNotExist:
                messages.error(request, f"No price found for {service.name} and {pet_size} dogs.")
                return render(request, 'core/book_appointment.html', {'form': form})
            appointment.status = 'pending'
            appointment.save()

            formatted = appointment.appointment_time.strftime("%H:%M on %d/%m/%Y")
            messages.success(request, f"Appointment booked for {formatted} and pending approval.")
            return redirect('client_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'core/book_appointment.html', {'form': form})


@user_passes_test(is_manager)
def approve_appointments(request):
    pending_appointments = Appointment.objects.filter(status='pending')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        selected_appointment = get_object_or_404(Appointment, id=appointment_id)

        form = AppointmentApprovalForm(request.POST, prefix=str(appointment_id))
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

                messages.success(request, f"Appointment approved and assigned to {selected_employee.user.username}.")
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

    approved_appointments = Appointment.objects.filter(status='approved').order_by('-appointment_time')

    return render(request, 'core/appointments_dashboard.html', {
        'appointment_forms': appointment_forms,
        'approved_appointments': approved_appointments,
    })


@require_GET
def fetch_available_slots(request):
    service_id = request.GET.get('service_id')
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    if not service_id or not start_str or not end_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        service = Service.objects.get(id=service_id)
        start_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
    except (Service.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    all_slots = []
    for date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        time_strings = get_available_slots(service, date)
        for time_str in time_strings:
            start_dt = timezone.make_aware(datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M"))
            end_dt = start_dt + service.duration
            all_slots.append({
                "title": "Available",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            })

    return JsonResponse(all_slots, safe=False)


@require_GET
def get_service_price(request):
    pet_id = request.GET.get('pet_id')
    service_id = request.GET.get('service_id')

    if not pet_id or not service_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        pet = PetProfile.objects.get(id=pet_id)
        service = Service.objects.get(id=service_id)
        price = service.get_price_for_size(pet.size)
        return JsonResponse({'price': f"{price:.2f}"})
    except (PetProfile.DoesNotExist, Service.DoesNotExist, ServicePrice.DoesNotExist):
        return JsonResponse({'error': 'Unable to calculate price'}, status=404)
