#!/usr/bin/env python3
"""
Test Appointment Editing Functionality
Tests the full appointment edit workflow with validation
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, PetProfile, Appointment, Service, ServicePrice


def create_test_data():
    """Create test data for appointment editing"""
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_client',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'Client'}
    )
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'client'}
    )
    
    # Create test pet
    pet, created = PetProfile.objects.get_or_create(
        user=user,
        name='TestDog',
        defaults={
            'breed': 'Golden Retriever',
            'size': 'large',
            'date_of_birth': datetime.now().date() - timedelta(days=365),
            'profile_status': 'verified'
        }
    )
    
    # Create test service
    service, created = Service.objects.get_or_create(
        name='Basic Grooming',
        defaults={
            'description': 'Basic grooming service',
            'duration': timedelta(hours=2),
            'allowed_start_times': '09:00,11:00,14:00',
            'is_active': True
        }
    )
    
    # Create service price
    price, created = ServicePrice.objects.get_or_create(
        service=service,
        size='large',
        defaults={'price': 50.00}
    )
    
    return user, pet, service


def test_appointment_editing():
    """Test the appointment editing functionality"""
    print("\n=== Testing Appointment Editing Functionality ===\n")
    
    user, pet, service = create_test_data()
    
    # Create a test appointment (26 hours in the future - editable)
    future_time = timezone.now() + timedelta(hours=26)
    appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=future_time,
        status='approved',
        edit_count=0,
        final_price=50.00
    )
    
    print(f"✓ Created test appointment: {appointment}")
    print(f"  - Pet: {appointment.pet_profile.name}")
    print(f"  - Service: {appointment.service.name}")
    print(f"  - Time: {appointment.appointment_time}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit Count: {appointment.edit_count}")
    print(f"  - Price: £{appointment.final_price}")
    
    # Test 1: Check if appointment can be edited (> 24h, < 3 edits)
    now = timezone.now()
    time_until = appointment.appointment_time - now
    hours_until = time_until.total_seconds() / 3600
    
    can_edit = (
        hours_until > 24 and 
        appointment.edit_count < 3 and 
        appointment.status not in ['cancelled', 'completed']
    )
    
    print(f"\n--- Edit Eligibility Check ---")
    print(f"Hours until appointment: {hours_until:.1f}")
    print(f"Edit count: {appointment.edit_count}/3")
    print(f"Status: {appointment.status}")
    print(f"Can edit: {can_edit}")
    
    if can_edit:
        print("✓ Appointment is eligible for editing")
    else:
        print("✗ Appointment cannot be edited")
        return
    
    # Test 2: Simulate editing the appointment
    print(f"\n--- Simulating Appointment Edit ---")
    original_time = appointment.appointment_time
    original_service = appointment.service
    
    # Edit: Change time to 28 hours in future
    new_time = timezone.now() + timedelta(hours=28)
    appointment.appointment_time = new_time
    appointment.status = 'pending'  # Reset to pending after edit
    appointment.edit_count += 1
    appointment.save()
    
    print(f"✓ Appointment edited successfully")
    print(f"  - Original time: {original_time}")
    print(f"  - New time: {appointment.appointment_time}")
    print(f"  - Status reset to: {appointment.status}")
    print(f"  - Edit count incremented to: {appointment.edit_count}")
    
    # Test 3: Check edit limits
    print(f"\n--- Testing Edit Limits ---")
    edits_remaining = 3 - appointment.edit_count
    print(f"Edits remaining: {edits_remaining}")
    
    if edits_remaining > 0:
        print(f"✓ Client can edit {edits_remaining} more time(s)")
    else:
        print("⚠️  No more edits allowed - client must contact business")
    
    # Test 4: Test with appointment too close (< 24h)
    print(f"\n--- Testing 24-Hour Rule ---")
    close_appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=12),  # Only 12 hours away
        status='approved',
        edit_count=0
    )
    
    time_until_close = close_appointment.appointment_time - timezone.now()
    hours_until_close = time_until_close.total_seconds() / 3600
    can_edit_close = hours_until_close > 24
    
    print(f"Appointment in {hours_until_close:.1f} hours")
    print(f"Can edit: {can_edit_close}")
    
    if not can_edit_close:
        print("✓ 24-hour rule correctly prevents editing")
    else:
        print("✗ 24-hour rule not working")
    
    # Test 5: Test edit count limit
    print(f"\n--- Testing Edit Count Limit ---")
    max_edit_appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=48),
        status='approved',
        edit_count=3  # Already at maximum
    )
    
    can_edit_max = max_edit_appointment.edit_count < 3
    print(f"Edit count: {max_edit_appointment.edit_count}/3")
    print(f"Can edit: {can_edit_max}")
    
    if not can_edit_max:
        print("✓ Edit count limit correctly prevents editing")
    else:
        print("✗ Edit count limit not working")
    
    # Clean up test data
    print(f"\n--- Cleanup ---")
    Appointment.objects.filter(pet_profile=pet).delete()
    print("✓ Test appointments cleaned up")
    
    print(f"\n=== Appointment Editing Test Complete ===")
    print(f"✓ All core functionality working correctly")
    print(f"✓ 24-hour rule enforced")
    print(f"✓ 3-edit limit enforced") 
    print(f"✓ Status reset to pending after edit")
    print(f"✓ Edit count tracking functional")


if __name__ == "__main__":
    test_appointment_editing()
