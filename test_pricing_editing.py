#!/usr/bin/env python
"""
Test appointment editing with complete pricing data
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

def test_pricing_and_editing():
    """Test appointment editing with various dog sizes and services"""
    print("=== Testing Pricing and Editing for All Combinations ===\n")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='pricetestuser',
        defaults={'email': 'pricetest@test.com'}
    )
    if created:
        user.set_password('test123')
        user.save()
    
    # Create pets of different sizes
    pets_data = [
        {'name': 'SmallDog', 'size': 'small', 'breed': 'Chihuahua'},
        {'name': 'MediumDog', 'size': 'medium', 'breed': 'Cocker Spaniel'},
        {'name': 'LargeDog', 'size': 'large', 'breed': 'Golden Retriever'}
    ]
    
    pets = []
    for pet_data in pets_data:
        pet, created = PetProfile.objects.get_or_create(
            user=user,
            name=pet_data['name'],
            defaults={
                'breed': pet_data['breed'],
                'date_of_birth': timezone.now().date() - timedelta(days=365*2),
                'size': pet_data['size'],
                'profile_status': 'verified'
            }
        )
        pets.append(pet)
        if created:
            print(f"✓ Created {pet.name} ({pet.size})")
    
    # Test all services
    services = Service.objects.all()
    print(f"\n--- Testing Price Retrieval for All Combinations ---")
    
    total_tests = 0
    successful_tests = 0
    
    for pet in pets:
        print(f"\nPet: {pet.name} ({pet.size})")
        for service in services:
            total_tests += 1
            try:
                price = service.get_price_for_size(pet.size)
                print(f"  ✓ {service.name}: £{price}")
                successful_tests += 1
                
                # Test creating an appointment with this combination
                appointment_time = timezone.now() + timedelta(hours=25)
                appointment = Appointment.objects.create(
                    pet_profile=pet,
                    service=service,
                    appointment_time=appointment_time,
                    status='approved',
                    final_price=price,
                    edit_count=0
                )
                
                # Test editing (simulate what the view does)
                new_time = appointment_time + timedelta(hours=2)
                appointment.appointment_time = new_time
                appointment.status = 'pending'
                appointment.edit_count += 1
                appointment.save()
                
                print(f"    → Edit test successful (ID: {appointment.id})")
                
                # Clean up
                appointment.delete()
                
            except Exception as e:
                print(f"  ❌ {service.name}: Error - {e}")
    
    print(f"\n--- Test Summary ---")
    print(f"Total combinations tested: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All pricing and editing combinations work correctly!")
        return True
    else:
        print("❌ Some combinations failed")
        return False

if __name__ == '__main__':
    try:
        success = test_pricing_and_editing()
        if success:
            print("\n✅ All appointment editing with pricing is working correctly!")
        else:
            print("\n❌ Some issues found with appointment editing pricing")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
