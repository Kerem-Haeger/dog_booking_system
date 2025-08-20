from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import json

from ..models import (
    Service, PetProfile, ServicePrice, Appointment, UserProfile, EmployeeCalendar
)
from ..utils import get_available_slots
from .roles import is_manager


@require_GET
def fetch_available_slots(request):
    """AJAX endpoint to fetch available appointment slots for a service"""
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
    today = timezone.now().date()
    current_time = timezone.now()

    date_range = (end_date - start_date).days + 1
    for date in (start_date + timedelta(n) for n in range(date_range)):
        # Only process dates that are today or in the future
        if date < today:
            continue

        time_strings = get_available_slots(service, date)
        for time_str in time_strings:
            start_dt = timezone.make_aware(
                datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            )

            # If it's today, only show slots that are in the future
            if date == today and start_dt <= current_time:
                continue

            end_dt = start_dt + service.duration
            all_slots.append({
                "title": "Available",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            })

    return JsonResponse(all_slots, safe=False)


@require_GET
def get_service_price(request):
    """AJAX endpoint to get service price for a specific pet size"""
    pet_id = request.GET.get('pet_id')
    service_id = request.GET.get('service_id')

    if not pet_id or not service_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        pet = PetProfile.objects.get(id=pet_id)
        service = Service.objects.get(id=service_id)
        price = service.get_price_for_size(pet.size)
        return JsonResponse({'price': f"{price:.2f}"})
    except (PetProfile.DoesNotExist, Service.DoesNotExist,
            ServicePrice.DoesNotExist):
        return JsonResponse({'error': 'Unable to calculate price'},
                            status=404)


@require_GET
def get_calendar_events(request):
    """AJAX endpoint to fetch calendar events for FullCalendar"""
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    employee_id = request.GET.get('employee_id')

    # Debug logging
    print(f"DEBUG: Received start={start_str}, end={end_str}")

    if not start_str or not end_str:
        return JsonResponse({'error': 'Missing start/end parameters'},
                            status=400)

    try:
        import re
        # Handle URL decoding issue where + becomes space
        # First restore + signs in timezone offsets
        if ' ' in start_str and 'T' in start_str:
            start_fixed = start_str.replace(' ', '+')
        else:
            start_fixed = start_str

        if ' ' in end_str and 'T' in end_str:
            end_fixed = end_str.replace(' ', '+')
        else:
            end_fixed = end_str

        print(f"DEBUG: Fixed start={start_fixed}, end={end_fixed}")

        # Remove timezone info (e.g., +01:00, -05:00, Z)
        start_clean = re.sub(r'[+-]\d{2}:\d{2}$|Z$', '', start_fixed)
        end_clean = re.sub(r'[+-]\d{2}:\d{2}$|Z$', '', end_fixed)

        print(f"DEBUG: Cleaned start={start_clean}, end={end_clean}")

        # Parse the cleaned datetime strings
        start_date = datetime.fromisoformat(start_clean)
        end_date = datetime.fromisoformat(end_clean)

        print(f"DEBUG: Parsed start={start_date}, end={end_date}")

        # Make timezone aware (assume UTC)
        start_date = timezone.make_aware(start_date, timezone.utc)
        end_date = timezone.make_aware(end_date, timezone.utc)

        print(f"DEBUG: Timezone aware start={start_date}, end={end_date}")

    except Exception as e:
        print(f"DEBUG: Error parsing dates: {e}")
        return JsonResponse({
            'error': f'Invalid date format: {str(e)}',
            'start_received': start_str,
            'end_received': end_str
        }, status=400)

    # Base query for appointments in the date range - exclude rejected appointments
    appointments = Appointment.objects.filter(
        appointment_time__gte=start_date,
        appointment_time__lte=end_date
    ).exclude(
        status__in=['rejected', 'canceled']  # Don't show rejected/canceled on calendar
    ).select_related('pet_profile__user', 'service', 'employee__user')

    print(f"DEBUG: Found {appointments.count()} appointments in date range")

    # Filter by employee if specified
    if employee_id and employee_id != 'all':
        try:
            employee_id = int(employee_id)
            appointments = appointments.filter(employee_id=employee_id)
            print(f"DEBUG: Filtered to {appointments.count()} appointments "
                  f"for employee {employee_id}")
        except (ValueError, TypeError):
            pass

    events = []
    now = timezone.now()

    for appointment in appointments:
        # Calculate end time
        end_time = appointment.appointment_time + appointment.service.duration

        # Check if appointment is in the past (send to frontend for color logic)
        is_past = appointment.appointment_time < now

        # Create employee name
        if appointment.employee:
            employee_name = (
                appointment.employee.user.get_full_name()
                if appointment.employee.user.get_full_name()
                else appointment.employee.user.username
            )
        else:
            employee_name = 'Unassigned'

        title = f"{appointment.pet_profile.name} - {appointment.service.name}"
        if appointment.employee:
            title += f" ({employee_name})"

        events.append({
            'id': appointment.id,
            'title': title,
            'start': appointment.appointment_time.isoformat(),
            'end': end_time.isoformat(),
            # Colors will be applied by JavaScript for better performance
            'extendedProps': {
                'status': appointment.status,
                'pet_name': appointment.pet_profile.name,
                'service': appointment.service.name,
                'employee': employee_name,
                'client': (appointment.pet_profile.user.get_full_name() or
                           appointment.pet_profile.user.username),
                'appointment_id': appointment.id,
                'is_past': is_past
            }
        })

    print(f"DEBUG: Returning {len(events)} events")

    # Return just the events array (FullCalendar expects this format)
    return JsonResponse(events, safe=False)


@require_GET
def debug_appointments(request):
    """Debug endpoint to check appointments"""
    from django.utils import timezone
    from datetime import timedelta

    # Get all appointments
    all_appointments = Appointment.objects.all().select_related(
        'pet_profile__user', 'service', 'employee__user'
    )

    debug_info = {
        'total_appointments': all_appointments.count(),
        'appointments': []
    }

    for appt in all_appointments:
        debug_info['appointments'].append({
            'id': appt.id,
            'pet_name': appt.pet_profile.name,
            'service': appt.service.name,
            'appointment_time': appt.appointment_time.isoformat(),
            'status': appt.status,
            'employee': (appt.employee.user.username
                         if appt.employee else 'Unassigned')
        })

    # Also check what date range we're looking at
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    debug_info['current_week'] = {
        'start': week_start.isoformat(),
        'end': week_end.isoformat(),
        'appointments_this_week': all_appointments.filter(
            appointment_time__gte=week_start,
            appointment_time__lte=week_end
        ).count()
    }

    return JsonResponse(debug_info, safe=False)


@require_http_methods(["POST"])
@user_passes_test(is_manager)
def approve_appointment_ajax(request):
    """AJAX endpoint to approve an appointment"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        employee_id = data.get('employee_id')

        if not appointment_id or not employee_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing appointment_id or employee_id'
            }, status=400)

        appointment = get_object_or_404(Appointment, id=appointment_id)
        employee = get_object_or_404(
            UserProfile, id=employee_id, role='employee'
        )

        # Additional validation: appointment must still be pending
        if appointment.status != 'pending':
            return JsonResponse({
                'success': False,
                'error': 'Appointment is no longer pending approval'
            }, status=400)

        # Check if employee is available at this time
        busy_calendar = EmployeeCalendar.objects.filter(
            user_profile=employee,
            scheduled_time=appointment.appointment_time
        ).exists()

        if busy_calendar:
            return JsonResponse({
                'success': False,
                'error': 'Employee is not available at this time'
            }, status=400)

        # Verify appointment time is still in the future
        if appointment.appointment_time <= timezone.now():
            return JsonResponse({
                'success': False,
                'error': 'Cannot approve appointments in the past'
            }, status=400)

        # Update appointment
        appointment.employee = employee
        appointment.status = 'approved'
        appointment.save()

        # Create calendar entry
        EmployeeCalendar.objects.create(
            user_profile=employee,
            appointment=appointment,
            scheduled_time=appointment.appointment_time,
            available_time=False
        )

        return JsonResponse({
            'success': True,
            'message': (f'Appointment approved and assigned to '
                        f'{employee.user.username}')
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_manager)
def reject_appointment_ajax(request):
    """AJAX endpoint to reject an appointment"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')

        if not appointment_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing appointment_id'
            }, status=400)

        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Update appointment status
        appointment.status = 'rejected'
        appointment.save()

        return JsonResponse({
            'success': True,
            'message': 'Appointment rejected successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_manager)
def get_available_employees(request):
    """Get available employees for a specific appointment time"""
    appointment_id = request.GET.get('appointment_id')

    print(f"DEBUG: get_available_employees called with appointment_id: {appointment_id}")

    if not appointment_id:
        print("DEBUG: No appointment_id provided")
        return JsonResponse({
            'success': False,
            'error': 'Missing appointment_id'
        }, status=400)

    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        print(f"DEBUG: Found appointment {appointment.id} at {appointment.appointment_time}")

        # Get employees who are busy due to overlapping appointments
        from ..utils import get_overlapping_appointments

        # Get overlapping approved appointments
        overlapping_appointments = get_overlapping_appointments(appointment)
        busy_employee_ids_appointments = [
            appt.employee.id
            for appt in overlapping_appointments
            if appt.employee
        ]

        # Also check EmployeeCalendar for exact time conflicts (legacy support)
        busy_employee_ids_calendar = EmployeeCalendar.objects.filter(
            scheduled_time=appointment.appointment_time,
            available_time=False
        ).values_list('user_profile_id', flat=True)

        # Combine both sources of busy employees
        all_busy_employee_ids = list(busy_employee_ids_calendar) + busy_employee_ids_appointments

        print(f"DEBUG: Busy from calendar: {list(busy_employee_ids_calendar)}")
        print(f"DEBUG: Busy from appointments: {list(busy_employee_ids_appointments)}")
        print(f"DEBUG: All busy employee IDs: {all_busy_employee_ids}")

        # Get available employees
        available_employees = UserProfile.objects.filter(
            role='employee'
        ).exclude(id__in=all_busy_employee_ids).select_related('user')

        print(f"DEBUG: Found {available_employees.count()} available employees")

        employees_data = []
        for employee in available_employees:
            employee_info = {
                'id': employee.id,
                'name': (employee.user.get_full_name() or
                         employee.user.username)
            }
            employees_data.append(employee_info)
            print(f"DEBUG: Employee {employee_info['id']}: {employee_info['name']}")

        current_employee_id = appointment.employee.id if appointment.employee else None
        print(f"DEBUG: Current employee ID: {current_employee_id}")

        response_data = {
            'success': True,
            'employees': employees_data,
            'current_employee': current_employee_id
        }

        print(f"DEBUG: Returning response with {len(employees_data)} employees")
        return JsonResponse(response_data)

    except Exception as e:
        print(f"DEBUG: Exception in get_available_employees: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_manager)
def reassign_appointment_ajax(request):
    """AJAX endpoint to reassign an approved appointment to different employee"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        new_employee_id = data.get('employee_id')

        print(f"DEBUG: Reassign request - appointment_id: {appointment_id}, "
              f"employee_id: {new_employee_id}")

        if not appointment_id or not new_employee_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing appointment_id or employee_id'
            }, status=400)

        appointment = get_object_or_404(Appointment, id=appointment_id)
        new_employee = get_object_or_404(
            UserProfile, id=new_employee_id, role='employee'
        )

        current_emp_id = (appointment.employee.id
                          if appointment.employee else None)
        print(f"DEBUG: Current employee: {current_emp_id}")
        print(f"DEBUG: New employee: {new_employee.id}")

        # Check if it's the same employee (no change needed)
        if (appointment.employee and
                appointment.employee.id == int(new_employee_id)):
            return JsonResponse({
                'success': True,
                'message': 'Appointment is already assigned to this employee'
            })

        # Check if new employee is available (but exclude current appointment)
        busy_calendar = EmployeeCalendar.objects.filter(
            user_profile=new_employee,
            scheduled_time=appointment.appointment_time
        ).exclude(appointment=appointment).exists()

        if busy_calendar:
            return JsonResponse({
                'success': False,
                'error': 'New employee is not available at this time'
            }, status=400)

        # Remove old calendar entry if exists
        if appointment.employee:
            EmployeeCalendar.objects.filter(
                appointment=appointment
            ).delete()

        # Update appointment
        appointment.employee = new_employee
        appointment.save()

        # Create new calendar entry
        EmployeeCalendar.objects.create(
            user_profile=new_employee,
            appointment=appointment,
            scheduled_time=appointment.appointment_time,
            available_time=False
        )

        employee_name = new_employee.user.username
        print(f"DEBUG: Successfully reassigned to {employee_name}")

        return JsonResponse({
            'success': True,
            'message': f'Appointment reassigned to {employee_name}'
        })

    except json.JSONDecodeError:
        print("DEBUG: JSON decode error")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"DEBUG: Exception occurred: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
