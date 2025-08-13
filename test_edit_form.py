#!/usr/bin/env python
"""
Test script to verify appointment editing form submission works correctly
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import PetProfile, Service, Appointment, ServicePrice

def test_edit_form_submission():
    """Test that the edit form processes correctly"""
    print("=== Testing Edit Form Submission ===\n")
    
    # Create test client
    client = Client()
    
    # Create test user (or get existing)
    try:
        user = User.objects.create_user(
            username='testclient',
            email='test@test.com',
            password='testpass123'
        )
        created_user = True
    except:
        user = User.objects.get(username='testclient')
        created_user = False    # Create test pet
    pet = PetProfile.objects.create(
        user=user,
        name='TestDog',
        breed='Golden Retriever',
        date_of_birth=timezone.now().date() - timedelta(days=365*3),  # 3 years old
        size='large',
        profile_status='approved'
    )
    
    # Create test service
    service = Service.objects.create(
        name='Basic Grooming',
        duration=timedelta(hours=2),
        is_active=True,
        slot_interval=30,
        allowed_start_times='09:00,11:00,13:00,15:00'
    )
    
    # Create service price
    ServicePrice.objects.create(
        service=service,
        size='large',
        price=50.00
    )
    
    # Create test appointment (25 hours in future - editable)
    appointment_time = timezone.now() + timedelta(hours=25)
    appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=appointment_time,
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"✓ Created test appointment: {appointment.id}")
    print(f"  - Pet: {pet.name}")
    print(f"  - Service: {service.name}")
    print(f"  - Time: {appointment_time}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit Count: {appointment.edit_count}")
    
    # Login
    login_success = client.login(username='testclient', password='testpass123')
    print(f"✓ Login successful: {login_success}")
    
    # Test GET request to edit form
    edit_url = reverse('edit_appointment', args=[appointment.id])
    get_response = client.get(edit_url)
    print(f"✓ GET edit form: Status {get_response.status_code}")
    
    if get_response.status_code == 200:
        print("  - Form loaded successfully")
        # Check if form contains expected elements
        content = get_response.content.decode()
        has_pet_field = 'id_pet_profile' in content
        has_service_field = 'id_service' in content
        has_time_field = 'id_time_slot' in content
        print(f"  - Pet field present: {has_pet_field}")
        print(f"  - Service field present: {has_service_field}")
        print(f"  - Time slot field present: {has_time_field}")
    
    # Test POST request (edit submission)
    new_time = appointment_time + timedelta(hours=2)  # Change to 2 hours later
    new_time_iso = new_time.isoformat()
    
    post_data = {
        'pet_profile': pet.id,
        'service': service.id,
        'time_slot': new_time_iso
    }
    
    print(f"\n--- Testing Form Submission ---")
    print(f"POST data: {post_data}")
    
    post_response = client.post(edit_url, data=post_data, follow=True)
    print(f"✓ POST edit form: Status {post_response.status_code}")
    
    # Check if redirected to dashboard
    final_url = post_response.request['PATH_INFO']
    print(f"✓ Final URL: {final_url}")
    
    # Check if appointment was updated
    appointment.refresh_from_db()
    print(f"\n--- Updated Appointment Details ---")
    print(f"  - New time: {appointment.appointment_time}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit count: {appointment.edit_count}")
    
    # Verify changes
    time_changed = appointment.appointment_time.replace(microsecond=0) == new_time.replace(microsecond=0)
    status_pending = appointment.status == 'pending'
    edit_count_incremented = appointment.edit_count == 1
    
    print(f"\n--- Verification ---")
    print(f"✓ Time changed correctly: {time_changed}")
    print(f"✓ Status reset to pending: {status_pending}")
    print(f"✓ Edit count incremented: {edit_count_incremented}")
    
    # Check for success message in response
    has_success_message = any('updated' in str(message).lower() for message in post_response.context.get('messages', []))
    print(f"✓ Success message present: {has_success_message}")
    
    # Cleanup (only if we created the user)
    if created_user:
        user.delete()
    else:
        # Just clean up test data
        appointment.delete()
        pet.delete()
        service.delete()
    print(f"\n✓ Cleanup completed")
    
    # Summary
    all_checks_passed = all([
        get_response.status_code == 200,
        post_response.status_code == 200,
        final_url == '/client/dashboard/',
        time_changed,
        status_pending,
        edit_count_incremented
    ])
    
    print(f"\n=== Test Summary ===")
    print(f"✓ All checks passed: {all_checks_passed}")
    
    return all_checks_passed

if __name__ == '__main__':
    success = test_edit_form_submission()
    if success:
        print("🎉 Edit form submission test PASSED!")
    else:
        print("❌ Edit form submission test FAILED!")
        sys.exit(1)
