from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import UserProfile, EmployeeCalendar, TimeOffRequest


def get_available_slots(service, date_obj):
    service_length = service.duration
    slots = []

    # Get predefined allowed start times from the service model
    allowed_times = service.get_allowed_times()  # e.g., ["09:00", "11:30", "14:00"]
    employees = UserProfile.objects.filter(role='employee')

    for time_str in allowed_times:
        try:
            start_time = make_aware(datetime.strptime(f"{date_obj} {time_str}", "%Y-%m-%d %H:%M"))
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
