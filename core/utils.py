from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import UserProfile, EmployeeCalendar, TimeOffRequest


def appointments_overlap(appointment1_start, appointment1_end, appointment2_start, appointment2_end):
    """
    Check if two appointments overlap in time.
    Returns True if there is any overlap, False otherwise.
    """
    # Two appointments overlap if one starts before the other ends
    # and the other starts before the first one ends
    return (appointment1_start < appointment2_end and 
            appointment2_start < appointment1_end)


def get_overlapping_appointments(target_appointment):
    """
    Get all approved appointments that overlap with the target appointment.
    Returns a queryset of overlapping appointments.
    """
    from .models import Appointment  # Import here to avoid circular imports
    
    target_start = target_appointment.appointment_time
    target_end = target_appointment.get_end_time()
    
    # Find all approved appointments that overlap with this time range
    overlapping = Appointment.objects.filter(
        status='approved',
        employee__isnull=False
    ).exclude(id=target_appointment.id)
    
    # Filter for actual overlaps - we need to check each one individually
    # because database doesn't have the calculated end time
    overlapping_appointments = []
    for appt in overlapping:
        appt_start = appt.appointment_time
        appt_end = appt.get_end_time()
        
        if appointments_overlap(target_start, target_end, appt_start, appt_end):
            overlapping_appointments.append(appt)
    
    return overlapping_appointments


def get_available_slots(service, date_obj):
    service_length = service.duration
    slots = []

    # Get predefined allowed start times from the service model
    allowed_times = service.get_allowed_times()  # ["09:00", "11:30", "14:00"]
    employees = UserProfile.objects.filter(role='employee')

    for time_str in allowed_times:
        try:
            datetime_str = f"{date_obj} {time_str}"
            start_time = make_aware(
                datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            )
            end_time = start_time + service_length
        except ValueError:
            continue  # Skip malformed times

        # Check if at least one employee is free
        for employee in employees:
            conflict = EmployeeCalendar.objects.filter(
                user_profile=employee,
                scheduled_time__lt=end_time,
                scheduled_time__gte=start_time
            ).exists()

            time_off = TimeOffRequest.objects.filter(
                user_profile=employee,
                status='approved',
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if not conflict and not time_off:
                slots.append(time_str)  # only append once (per time)
                break  # no need to check other employees

    return slots
