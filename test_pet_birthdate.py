#!/usr/bin/env python3
"""
Simple test for Pet Profile birth date validation
"""
import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from core.forms import PetProfileForm

def test_birthdate_validation():
    print("=== Testing Pet Birth Date Validation ===")
    
    # Test 1: Future date (should be invalid)
    print("\n1. Testing future date...")
    future_date = date.today() + timedelta(days=10)
    form_data = {
        'name': 'Test Pet',
        'breed': 'Test Breed', 
        'date_of_birth': future_date,
        'grooming_preferences': 'Test preferences'
    }
    
    form = PetProfileForm(data=form_data)
    print(f"Future date ({future_date}): Valid = {form.is_valid()}")
    if not form.is_valid():
        if 'date_of_birth' in form.errors:
            print(f"✅ Correctly caught error: {form.errors['date_of_birth'][0]}")
        else:
            print(f"❌ Other errors: {form.errors}")
    else:
        print("❌ Should have been invalid!")
    
    # Test 2: Valid past date (should be valid)
    print("\n2. Testing valid past date...")
    past_date = date.today() - timedelta(days=365)
    form_data['date_of_birth'] = past_date
    form2 = PetProfileForm(data=form_data)
    print(f"Past date ({past_date}): Valid = {form2.is_valid()}")
    if form2.is_valid():
        print("✅ Past date correctly validated!")
    else:
        print(f"❌ Unexpected errors: {form2.errors}")
    
    # Test 3: Today's date (should be valid)
    print("\n3. Testing today's date...")
    today = date.today()
    form_data['date_of_birth'] = today
    form3 = PetProfileForm(data=form_data)
    print(f"Today's date ({today}): Valid = {form3.is_valid()}")
    if form3.is_valid():
        print("✅ Today's date correctly validated!")
    else:
        print(f"❌ Unexpected errors: {form3.errors}")

if __name__ == "__main__":
    test_birthdate_validation()
