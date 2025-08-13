#!/usr/bin/env python
"""
Complete appointment editing integration test
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
from core.views.client_views import edit_appointment
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

def test_full_edit_process():
    """Test the complete edit appointment process"""
    print("=== Complete Edit Process Test ===\n")
    
    # Create/get test user
    user, created = User.objects.get_or_create(
        username='testedit',
        defaults={'email': 'testedit@test.com'}
    )
    if created:
        user.set_password('test123')
        user.save()
        print("✓ Created test user")
    else:
        print("✓ Using existing test user")
    
    # Create test data
    pet = PetProfile.objects.create(
        user=user,
        name='EditTestDog',
        breed='Labrador',
        date_of_birth=timezone.now().date() - timedelta(days=365*2),
        size='large',
        profile_status='verified'
    )
    
    service = Service.objects.create(
        name='Edit Test Grooming',
        duration=timedelta(hours=1, minutes=30),
        is_active=True,
        slot_interval=30,
        allowed_start_times='09:00,11:00,13:00,15:00'
    )
    
    ServicePrice.objects.create(
        service=service,
        size='large',
        price=55.00
    )
    
    # Create appointment 26 hours in future (editable)
    original_time = timezone.now() + timedelta(hours=26)
    appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=original_time,
        status='approved',
        final_price=55.00,
        edit_count=0
    )
    
    print(f"✓ Created test appointment ID: {appointment.id}")
    print(f"  - Original time: {original_time}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit count: {appointment.edit_count}")
    
    # Test 1: Verify form sees the pet (queryset test)
    print(f"\n--- Test 1: Form Queryset ---")
    form = AppointmentForm(user=user, instance=appointment)
    pet_choices = list(form.fields['pet_profile'].queryset)
    print(f"✓ Available pets: {[p.name for p in pet_choices]}")
    has_our_pet = pet in pet_choices
    print(f"✓ Our pet in choices: {has_our_pet}")
    
    if not has_our_pet:
        print("❌ Pet not available in form - checking pet status")
        print(f"  Pet status: {pet.profile_status}")
        print(f"  Pet user: {pet.user}")
        print("  This would cause form validation to fail")
    
    # Test 2: Form validation with correct data
    print(f"\n--- Test 2: Form Validation ---")
    new_time = original_time + timedelta(hours=3)
    form_data = {
        'pet_profile': pet.id,
        'service': service.id,
        'time_slot': new_time.isoformat(),
        'voucher_code': ''
    }
    
    form = AppointmentForm(data=form_data, user=user, instance=appointment)
    is_valid = form.is_valid()
    print(f"✓ Form valid: {is_valid}")
    
    if not is_valid:
        print(f"  - Errors: {dict(form.errors)}")
        return False
    
    print(f"  - Cleaned time_slot: {form.cleaned_data.get('time_slot')}")
    
    # Test 3: Manual save process (what the view does)
    print(f"\n--- Test 3: Manual Save Process ---")
    try:
        updated_appointment = form.save(commit=False)
        
        # Set the time_slot manually (like the view does)
        time_slot_str = form.cleaned_data.get('time_slot')
        if time_slot_str.endswith("Z"):
            time_slot_str = time_slot_str.rstrip("Z")
        
        # Parse the datetime string
        parsed_datetime = datetime.fromisoformat(time_slot_str)
        
        # Check if it's naive or aware
        if timezone.is_naive(parsed_datetime):
            combined_datetime = timezone.make_aware(parsed_datetime)
        else:
            combined_datetime = parsed_datetime
        
        updated_appointment.appointment_time = combined_datetime
        
        # Set other fields like the view does
        service_obj = updated_appointment.service
        pet_size = updated_appointment.pet_profile.size
        updated_appointment.final_price = service_obj.get_price_for_size(pet_size)
        updated_appointment.status = 'pending'
        updated_appointment.edit_count += 1
        
        # Save
        updated_appointment.save()
        
        print(f"✓ Save successful")
        print(f"  - New time: {updated_appointment.appointment_time}")
        print(f"  - Status: {updated_appointment.status}")
        print(f"  - Edit count: {updated_appointment.edit_count}")
        print(f"  - Price: {updated_appointment.final_price}")
        
        # Verify the change worked
        appointment.refresh_from_db()
        time_changed = appointment.appointment_time.replace(microsecond=0) == new_time.replace(microsecond=0)
        status_pending = appointment.status == 'pending'
        edit_incremented = appointment.edit_count == 1
        
        print(f"\n--- Verification ---")
        print(f"✓ Time changed: {time_changed}")
        print(f"✓ Status pending: {status_pending}")
        print(f"✓ Edit count incremented: {edit_incremented}")
        
        success = all([time_changed, status_pending, edit_incremented])
        
    except Exception as e:
        print(f"❌ Save failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    # Cleanup
    appointment.delete()
    pet.delete()
    service.delete()
    if created:
        user.delete()
    
    print(f"\n✓ Cleanup completed")
    print(f"\n=== Overall Result: {'PASS' if success else 'FAIL'} ===")
    
    return success

if __name__ == '__main__':
    try:
        from datetime import datetime
        success = test_full_edit_process()
        if success:
            print("🎉 Complete edit process test PASSED!")
        else:
            print("❌ Complete edit process test FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
