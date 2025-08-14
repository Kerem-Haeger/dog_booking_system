#!/usr/bin/env python3
"""Debug script to check appointment statuses"""

import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from core.models import Appointment
from django.utils import timezone

print("=== APPOINTMENT STATUS DEBUG ===\n")

# Get all appointments
all_appointments = Appointment.objects.all().order_by('-appointment_time')

print(f"Total appointments in system: {all_appointments.count()}\n")

if all_appointments.exists():
    print("All appointments:")
    for appt in all_appointments:
        print(f"  - {appt.pet_profile.name} - {appt.service.name}")
        print(f"    Time: {appt.appointment_time}")
        print(f"    Status: {appt.status}")
        print(f"    Client: {appt.pet_profile.user.username}")
        print()

    # Check current time
    now = timezone.now()
    print(f"Current time: {now}")
    print()

    # Check past vs future
    past_appointments = Appointment.objects.filter(appointment_time__lt=now)
    future_appointments = Appointment.objects.filter(appointment_time__gte=now)
    
    print(f"Past appointments (any status): {past_appointments.count()}")
    print(f"Future appointments (any status): {future_appointments.count()}")
    print()
    
    # Check filtered past appointments
    filtered_past = Appointment.objects.filter(
        appointment_time__lt=now,
        status__in=['completed', 'canceled', 'approved']
    )
    print(f"Past appointments (completed/canceled/approved): {filtered_past.count()}")
    
    if filtered_past.exists():
        print("Filtered past appointments:")
        for appt in filtered_past:
            print(f"  - {appt.pet_profile.name} - {appt.service.name} ({appt.status})")
    
    # Check rejected appointments
    rejected_appointments = Appointment.objects.filter(status='rejected')
    print(f"\nRejected appointments: {rejected_appointments.count()}")
    if rejected_appointments.exists():
        print("Rejected appointments:")
        for appt in rejected_appointments:
            print(f"  - {appt.pet_profile.name} - {appt.service.name}")
            print(f"    Time: {appt.appointment_time}")

else:
    print("No appointments found in the system.")
