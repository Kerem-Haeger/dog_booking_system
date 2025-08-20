from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from ..models import Appointment, UserProfile


@login_required
def employee_dashboard(request):
    """Dashboard view for employees"""
    user_profile = UserProfile.objects.get(user=request.user)

    # Get today's appointments for this employee
    today = timezone.now().date()
    today_start = timezone.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_end = timezone.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    today_appointments = Appointment.objects.filter(
        employee=user_profile,
        appointment_time__range=(today_start, today_end)
    ).order_by('appointment_time')

    # Get upcoming appointments (next 7 days)
    next_week = today_start + timedelta(days=7)
    upcoming_appointments = Appointment.objects.filter(
        employee=user_profile,
        appointment_time__gt=today_end,
        appointment_time__lte=next_week
    ).order_by('appointment_time')[:5]

    context = {
        'user_profile': user_profile,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'today': today,
    }

    return render(request, 'core/dashboard/employee_dashboard.html', context)
