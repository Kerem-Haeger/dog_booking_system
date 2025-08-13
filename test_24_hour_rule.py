#!/usr/bin/env python
"""
Test 24-hour rule for appointment editing and cancelling
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

def test_24_hour_rule():
    """Test that 24-hour rule is properly enforced"""
    print("=== Testing 24-Hour Rule Enforcement ===\n")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='24htest',
        defaults={'email': '24htest@test.com'}
    )
    if created:
        user.set_password('test123')
        user.save()
    
    # Create test pet
    pet, created = PetProfile.objects.get_or_create(
        user=user,
        name='Test24Dog',
        defaults={
            'breed': 'Test Breed',
            'date_of_birth': timezone.now().date() - timedelta(days=365*2),
            'size': 'medium',
            'profile_status': 'verified'
        }
    )
    
    # Get a service
    service = Service.objects.first()
    if not service:
        print("❌ No services found")
        return False
    
    print("--- Test Cases ---")
    
    # Test Case 1: Appointment 30 hours away (should be editable)
    appointment_30h = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=30),
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"1. Appointment 30h away:")
    print(f"   can_edit: {appointment_30h.can_edit}")
    print(f"   can_cancel: {appointment_30h.can_cancel}")
    print(f"   ✓ Expected: Both True")
    
    # Test Case 2: Appointment 12 hours away (should NOT be editable)
    appointment_12h = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=12),
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"\n2. Appointment 12h away:")
    print(f"   can_edit: {appointment_12h.can_edit}")
    print(f"   can_cancel: {appointment_12h.can_cancel}")
    print(f"   ✓ Expected: Both False")
    
    # Test Case 3: Appointment exactly 24 hours away
    appointment_24h = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=24),
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"\n3. Appointment exactly 24h away:")
    print(f"   can_edit: {appointment_24h.can_edit}")
    print(f"   can_cancel: {appointment_24h.can_cancel}")
    print(f"   ✓ Expected: Both False (24h rule is <=24h)")
    
    # Test Case 4: Appointment with 3 edits (should not be editable regardless of time)
    appointment_max_edits = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=48),
        status='approved',
        final_price=50.00,
        edit_count=3  # Max edits reached
    )
    
    print(f"\n4. Appointment 48h away but 3/3 edits used:")
    print(f"   can_edit: {appointment_max_edits.can_edit}")
    print(f"   can_cancel: {appointment_max_edits.can_cancel}")
    print(f"   ✓ Expected: can_edit=False, can_cancel=True")
    
    # Test Case 5: Cancelled appointment
    appointment_cancelled = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=timezone.now() + timedelta(hours=48),
        status='cancelled',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"\n5. Cancelled appointment:")
    print(f"   can_edit: {appointment_cancelled.can_edit}")
    print(f"   can_cancel: {appointment_cancelled.can_cancel}")
    print(f"   ✓ Expected: Both False")
    
    # Verify results
    test_results = [
        appointment_30h.can_edit and appointment_30h.can_cancel,  # Case 1
        not appointment_12h.can_edit and not appointment_12h.can_cancel,  # Case 2
        not appointment_24h.can_edit and not appointment_24h.can_cancel,  # Case 3
        not appointment_max_edits.can_edit and appointment_max_edits.can_cancel,  # Case 4
        not appointment_cancelled.can_edit and not appointment_cancelled.can_cancel  # Case 5
    ]
    
    # Cleanup
    Appointment.objects.filter(pet_profile=pet).delete()
    if created:
        pet.delete()
        user.delete()
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n--- Results ---")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All 24-hour rule tests PASSED!")
        return True
    else:
        print("❌ Some 24-hour rule tests FAILED!")
        return False

if __name__ == '__main__':
    try:
        success = test_24_hour_rule()
        if success:
            print("\n✅ 24-hour rule is properly enforced!")
        else:
            print("\n❌ 24-hour rule enforcement has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
