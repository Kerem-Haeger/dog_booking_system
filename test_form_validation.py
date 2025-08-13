#!/usr/bin/env python
"""
Test the AppointmentForm directly to debug validation issues
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import PetProfile, Service, Appointment, ServicePrice
from core.forms import AppointmentForm

def test_appointment_form():
    """Test AppointmentForm validation directly"""
    print("=== Testing AppointmentForm Validation ===\n")
    
    # Get test user
    try:
        user = User.objects.get(username='testclient')
        print("✓ Using existing test user")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testclient',
            password='testpass123',
            email='test@test.com'
        )
        print("✓ Created new test user")
    
    # Create test data
    pet = PetProfile.objects.create(
        user=user,
        name='TestDog',
        breed='Golden Retriever',
        date_of_birth=timezone.now().date() - timedelta(days=365*3),
        size='large',
        profile_status='verified'  # Use verified instead of approved
    )
    
    service = Service.objects.create(
        name='Basic Grooming',
        duration=timedelta(hours=2),
        is_active=True,
        slot_interval=30,
        allowed_start_times='09:00,11:00,13:00,15:00'
    )
    
    ServicePrice.objects.create(
        service=service,
        size='large',
        price=50.00
    )
    
    # Create test appointment
    appointment_time = timezone.now() + timedelta(hours=25)
    appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=appointment_time,
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"✓ Created test data")
    print(f"  - Pet: {pet.name} (ID: {pet.id})")
    print(f"  - Service: {service.name} (ID: {service.id})")
    print(f"  - Appointment: ID {appointment.id}")
    
    # Test form with edit data
    new_time = appointment_time + timedelta(hours=2)
    form_data = {
        'pet_profile': pet.id,
        'service': service.id,
        'time_slot': new_time.isoformat()
    }
    
    print(f"\n--- Testing Form Validation ---")
    print(f"Form data: {form_data}")
    
    # Create form instance for editing
    form = AppointmentForm(data=form_data, user=user, instance=appointment)
    
    print(f"✓ Form created")
    print(f"  - Is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"  - Errors: {form.errors}")
        print(f"  - Non-field errors: {form.non_field_errors()}")
    else:
        print(f"  - Cleaned data: {form.cleaned_data}")
        
        # Try to save
        try:
            updated_appointment = form.save(commit=False)
            print(f"✓ Form save (commit=False) successful")
            print(f"  - Pet: {updated_appointment.pet_profile}")
            print(f"  - Service: {updated_appointment.service}")
        except Exception as e:
            print(f"❌ Form save failed: {e}")
    
    # Test without time_slot to see if that's the issue
    print(f"\n--- Testing Form Without Time Slot ---")
    form_data_no_time = {
        'pet_profile': pet.id,
        'service': service.id,
        'time_slot': ''  # Empty time slot
    }
    
    form2 = AppointmentForm(data=form_data_no_time, user=user, instance=appointment)
    print(f"✓ Form without time slot - Is valid: {form2.is_valid()}")
    if not form2.is_valid():
        print(f"  - Errors: {form2.errors}")
    
    # Cleanup
    appointment.delete()
    pet.delete()
    service.delete()
    print(f"\n✓ Cleanup completed")

if __name__ == '__main__':
    try:
        test_appointment_form()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
