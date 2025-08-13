#!/usr/bin/env python3
"""
Test script to verify that grooming preferences have been removed from client-side forms
while still maintaining the field in the model for manager/employee use.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_system.settings')
django.setup()

from core.forms import PetProfileForm, PetProfileManagerForm
from core.models import PetProfile
from django.contrib.auth.models import User


def test_client_form_excludes_grooming_preferences():
    """Test that client PetProfileForm excludes grooming preferences"""
    print("Testing client form (PetProfileForm)...")
    
    form = PetProfileForm()
    
    # Check that grooming_preferences is NOT in the form fields
    if 'grooming_preferences' not in form.fields:
        print("✅ Client form correctly excludes grooming_preferences field")
    else:
        print("❌ Client form still includes grooming_preferences field")
        return False
    
    # Check that essential fields are still present
    expected_fields = ['name', 'breed', 'date_of_birth']
    for field in expected_fields:
        if field in form.fields:
            print(f"✅ Client form includes {field} field")
        else:
            print(f"❌ Client form missing {field} field")
            return False
    
    return True


def test_manager_form_includes_grooming_preferences():
    """Test that manager PetProfileManagerForm includes grooming preferences"""
    print("\nTesting manager form (PetProfileManagerForm)...")
    
    form = PetProfileManagerForm()
    
    # Check that grooming_preferences IS in the manager form fields
    if 'grooming_preferences' in form.fields:
        print("✅ Manager form correctly includes grooming_preferences field")
    else:
        print("❌ Manager form missing grooming_preferences field")
        return False
    
    # Check that all fields are present
    expected_fields = ['name', 'breed', 'date_of_birth', 'grooming_preferences', 'size', 'profile_status']
    for field in expected_fields:
        if field in form.fields:
            print(f"✅ Manager form includes {field} field")
        else:
            print(f"❌ Manager form missing {field} field")
            return False
    
    return True


def test_model_still_has_grooming_preferences():
    """Test that the PetProfile model still has the grooming_preferences field"""
    print("\nTesting model field presence...")
    
    # Check that the model still has the grooming_preferences field
    if hasattr(PetProfile, 'grooming_preferences'):
        print("✅ PetProfile model still has grooming_preferences field")
    else:
        print("❌ PetProfile model missing grooming_preferences field")
        return False
    
    return True


def test_form_submission():
    """Test that client form can be submitted without grooming preferences"""
    print("\nTesting form submission...")
    
    # Test data without grooming preferences
    form_data = {
        'name': 'Test Dog',
        'breed': 'Golden Retriever',
        'date_of_birth': '2020-01-01'
    }
    
    form = PetProfileForm(data=form_data)
    
    if form.is_valid():
        print("✅ Client form validates successfully without grooming_preferences")
        return True
    else:
        print("❌ Client form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING GROOMING PREFERENCES REMOVAL")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Run all tests
    tests = [
        test_client_form_excludes_grooming_preferences,
        test_manager_form_includes_grooming_preferences,
        test_model_still_has_grooming_preferences,
        test_form_submission
    ]
    
    for test in tests:
        try:
            if not test():
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Grooming preferences successfully removed from client side.")
        print("✅ Field is preserved in model for future manager/employee use.")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
