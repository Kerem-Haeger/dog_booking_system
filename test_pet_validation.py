#!/usr/bin/env python3
"""
Test script for Pet Profile birth date validation
"""
import os
import sys
import django
from datetime import date, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.forms import PetProfileForm
from core.models import PetProfile


def test_pet_birth_date_validation():
    """Test pet profile birth date validation"""
    print("Testing Pet Profile Birth Date Validation")
    print("=" * 50)
    
    # Test data
    today = date.today()
    future_date = today + timedelta(days=10)
    past_date = today - timedelta(days=365)  # 1 year ago
    very_old_date = today - timedelta(days=365 * 35)  # 35 years ago
    
    test_cases = [
        {
            'name': 'Valid past date',
            'data': {
                'name': 'Buddy',
                'breed': 'Golden Retriever',
                'date_of_birth': past_date,
                'grooming_preferences': 'Gentle grooming please'
            },
            'should_be_valid': True
        },
        {
            'name': 'Future date (invalid)',
            'data': {
                'name': 'Max',
                'breed': 'Labrador',
                'date_of_birth': future_date,
                'grooming_preferences': 'Regular grooming'
            },
            'should_be_valid': False,
            'expected_error': 'Birth date cannot be in the future.'
        },
        {
            'name': 'Very old date (invalid)',
            'data': {
                'name': 'Old Dog',
                'breed': 'Beagle',
                'date_of_birth': very_old_date,
                'grooming_preferences': 'Special care needed'
            },
            'should_be_valid': False,
            'expected_error': 'Birth date cannot be more than 30 years ago.'
        },
        {
            'name': 'Today\'s date (valid)',
            'data': {
                'name': 'Puppy',
                'breed': 'Poodle',
                'date_of_birth': today,
                'grooming_preferences': 'First grooming'
            },
            'should_be_valid': True
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Birth date: {test_case['data']['date_of_birth']}")
        
        form = PetProfileForm(data=test_case['data'])
        is_valid = form.is_valid()
        
        if test_case['should_be_valid']:
            if is_valid:
                print("✅ PASS - Form is valid as expected")
            else:
                print("❌ FAIL - Form should be valid but isn't")
                print(f"   Errors: {form.errors}")
        else:
            if not is_valid:
                print("✅ PASS - Form is invalid as expected")
                if 'date_of_birth' in form.errors:
                    error_msg = str(form.errors['date_of_birth'][0])
                    if test_case['expected_error'] in error_msg:
                        print(f"   ✅ Correct error message: {error_msg}")
                    else:
                        print(f"   ⚠️  Different error message: {error_msg}")
                        print(f"   Expected: {test_case['expected_error']}")
                else:
                    print(f"   ⚠️  No date_of_birth error found: {form.errors}")
            else:
                print("❌ FAIL - Form should be invalid but is valid")
    
    print(f"\n{'='*50}")
    print("Birth date validation test completed!")


if __name__ == "__main__":
    test_pet_birth_date_validation()
