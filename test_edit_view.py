#!/usr/bin/env python
"""
Simple test to verify edit appointment view functions correctly
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
from core.views.client_views import edit_appointment
from django.test import RequestFactory
from django.contrib.auth import authenticate, login
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages import get_messages

def test_edit_appointment_view():
    """Test edit appointment view logic directly"""
    print("=== Testing Edit Appointment View Logic ===\n")
    
    # Get or create test user
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
    
    # Create editable appointment (25+ hours in future)
    appointment_time = timezone.now() + timedelta(hours=25)
    appointment = Appointment.objects.create(
        pet_profile=pet,
        service=service,
        appointment_time=appointment_time,
        status='approved',
        final_price=50.00,
        edit_count=0
    )
    
    print(f"✓ Created test appointment: ID {appointment.id}")
    print(f"  - Time: {appointment_time}")
    print(f"  - Hours until: {(appointment_time - timezone.now()).total_seconds() / 3600:.1f}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit count: {appointment.edit_count}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test GET request
    print("\n--- Testing GET Request ---")
    request = factory.get(f'/client/appointments/{appointment.id}/edit/')
    request.user = user
    
    # Add session and message middleware
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    
    response = edit_appointment(request, appointment.id)
    print(f"✓ GET response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Edit form rendered successfully")
    
    # Test POST request with valid data
    print("\n--- Testing POST Request ---")
    new_time = appointment_time + timedelta(hours=2)
    post_data = {
        'pet_profile': pet.id,
        'service': service.id,
        'time_slot': new_time.isoformat()
    }
    
    request = factory.post(f'/client/appointments/{appointment.id}/edit/', data=post_data)
    request.user = user
    
    # Add session and message middleware
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    
    response = edit_appointment(request, appointment.id)
    print(f"✓ POST response status: {response.status_code}")
    
    # Print debug info right after the view call
    if hasattr(response, 'content'):
        content = response.content.decode()
        if 'form-errors' in content or 'error' in content.lower():
            print("⚠️  Form may have validation errors")
        # Look for actual error messages in HTML
        if 'errorlist' in content:
            import re
            errors = re.findall(r'<li>(.*?)</li>', content)
            print(f"  - Found errors: {errors[:3]}")  # Show first 3 errors
    
    # Check if appointment was updated
    appointment.refresh_from_db()
    print(f"\n--- Updated Appointment ---")
    print(f"  - New time: {appointment.appointment_time}")
    print(f"  - Status: {appointment.status}")
    print(f"  - Edit count: {appointment.edit_count}")
    
    # Verify changes
    time_updated = appointment.appointment_time.replace(microsecond=0) == new_time.replace(microsecond=0)
    status_pending = appointment.status == 'pending'
    edit_incremented = appointment.edit_count == 1
    
    print(f"\n--- Verification ---")
    print(f"✓ Time updated: {time_updated}")
    print(f"✓ Status reset to pending: {status_pending}")
    print(f"✓ Edit count incremented: {edit_incremented}")
    
    # Check response type (should be redirect)
    is_redirect = response.status_code in [301, 302]
    print(f"✓ Redirects to dashboard: {is_redirect}")
    
    # Cleanup
    appointment.delete()
    pet.delete() 
    service.delete()
    print(f"\n✓ Cleanup completed")
    
    # Overall result
    success = all([
        response.status_code in [200, 302],  # GET 200 or POST redirect
        time_updated,
        status_pending,
        edit_incremented
    ])
    
    print(f"\n=== Test Result ===")
    print(f"✓ Edit functionality working: {success}")
    
    return success

if __name__ == '__main__':
    try:
        success = test_edit_appointment_view()
        if success:
            print("🎉 Edit appointment view test PASSED!")
        else:
            print("❌ Edit appointment view test FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
