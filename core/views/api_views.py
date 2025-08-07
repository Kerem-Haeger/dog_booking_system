from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import (
    Service, PetProfile, ServicePrice, Appointment
)
from ..utils import get_available_slots


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
    date_range = (end_date - start_date).days + 1
    for date in (start_date + timedelta(n) for n in range(date_range)):
        time_strings = get_available_slots(service, date)
        for time_str in time_strings:
            start_dt = timezone.make_aware(
                datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            )
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

    # Base query for appointments in the date range
    appointments = Appointment.objects.filter(
        appointment_time__gte=start_date,
        appointment_time__lte=end_date
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
    for appointment in appointments:
        # Calculate end time
        end_time = appointment.appointment_time + appointment.service.duration
        
        # Set color based on status
        if appointment.status == 'approved':
            bg_color = '#28a745'  # Green
            border_color = '#28a745'
        elif appointment.status == 'pending':
            bg_color = '#ffc107'  # Yellow
            border_color = '#ffc107'
        elif appointment.status == 'completed':
            bg_color = '#6c757d'  # Gray
            border_color = '#6c757d'
        else:  # canceled, rejected
            bg_color = '#dc3545'  # Red
            border_color = '#dc3545'

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
            'backgroundColor': bg_color,
            'borderColor': border_color,
            'extendedProps': {
                'status': appointment.status,
                'pet_name': appointment.pet_profile.name,
                'service': appointment.service.name,
                'employee': employee_name,
                'client': (appointment.pet_profile.user.get_full_name() or
                           appointment.pet_profile.user.username),
                'appointment_id': appointment.id
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
