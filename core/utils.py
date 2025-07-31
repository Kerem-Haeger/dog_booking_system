import datetime
from datetime import timedelta, time
from django.utils import timezone
from .models import UserProfile, EmployeeCalendar

BUSINESS_HOURS = {
    "open": time(9, 0),   # 09:00
    "close": time(18, 0),  # 18:00
}
BUSINESS_DAYS = [0, 1, 2, 3, 4, 5]  # Monday–Saturday (0=Mon, 6=Sun)


def get_available_slots(service, date):
    """
    Returns a list of available start times (as strings like '09:00')
    for a given service and date where at least one employee is free.
    """

    if date.weekday() not in BUSINESS_DAYS:
        return []

    slots = []
    slot_interval = timedelta(minutes=service.slot_interval)
    duration = service.duration

    start_time = timezone.make_aware(datetime.datetime.combine(date, BUSINESS_HOURS["open"]))
    end_time = timezone.make_aware(datetime.datetime.combine(date, BUSINESS_HOURS["close"]))

    while start_time + duration <= end_time:
        conflict_exists = EmployeeCalendar.objects.filter(
            scheduled_time__gte=start_time,
            scheduled_time__lt=start_time + duration
        ).exists()

        if not conflict_exists:
            slots.append(start_time.strftime('%H:%M'))

        start_time += slot_interval

    return slots
