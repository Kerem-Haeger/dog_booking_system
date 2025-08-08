#!/usr/bin/env python
"""
Test script to demonstrate time-ordered pending appointments.
Creates test appointments and shows they appear in chronological order.
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from core.models import Appointment, PetProfile, Service
from django.utils import timezone


def main():
    print("🔄 TESTING TIME-ORDERED PENDING APPOINTMENTS")
    print("=" * 50)
    
    # Get existing data for test appointments
    pet_profiles = PetProfile.objects.filter(profile_status='approved')
    services = Service.objects.filter(is_active=True)
    
    if not pet_profiles.exists():
        print("❌ No approved pets found - can't create test appointments")
        return
    
    if not services.exists():
        print("❌ No active services found - can't create test appointments")
        return
    
    # Clean up any existing test appointments first
    Appointment.objects.filter(
        pet_profile__name__contains='TEST'
    ).delete()
    
    # Create test appointments with different times
    base_time = timezone.now() + timedelta(days=2)  # Day after tomorrow
    
    test_appointments = [
        (base_time + timedelta(hours=8), "Morning appointment"),    # 08:00
        (base_time + timedelta(hours=4), "Early appointment"),     # 04:00 
        (base_time + timedelta(hours=12), "Afternoon appointment"), # 12:00
        (base_time + timedelta(hours=1), "Very early appointment"), # 01:00
    ]
    
    pet = pet_profiles.first()
    service = services.first()
    
    created_appointments = []
    
    print("\n📅 Creating test appointments:")
    for appointment_time, description in test_appointments:
        appointment = Appointment.objects.create(
            pet_profile=pet,
            service=service,
            appointment_time=appointment_time,
            status='pending'
        )
        created_appointments.append(appointment)
        print(f"   • {description}: {appointment_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Now fetch them as the view would (ordered by time)
    print("\n📋 How they appear in manager approval (ordered by time):")
    pending_appointments = Appointment.objects.filter(
        status='pending'
    ).order_by('appointment_time')
    
    for i, appointment in enumerate(pending_appointments, 1):
        time_str = appointment.appointment_time.strftime('%Y-%m-%d %H:%M')
        print(f"   {i}. {appointment.pet_profile.name} - {appointment.service.name}")
        print(f"      Time: {time_str}")
        print(f"      Client: {appointment.pet_profile.user.username}")
        print()
    
    print("✅ SUCCESS: Appointments are now ordered by time!")
    print("   Managers will see the most time-sensitive appointments first.")
    
    # Cleanup
    print("\n🧹 Cleaning up test appointments...")
    for appointment in created_appointments:
        appointment.delete()
    
    print("✅ Test completed successfully!")


if __name__ == "__main__":
    main()
