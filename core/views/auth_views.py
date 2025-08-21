"""
Dog Booking System
Author: Kerem Haeger
Created: August 2025
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from ..forms import CustomUserRegistrationForm
from ..models import UserProfile


def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Use transaction to ensure both User and UserProfile
                # are created
                with transaction.atomic():
                    # Create the user
                    user = form.save()

                    # Create UserProfile with 'pending' role
                    UserProfile.objects.create(
                        user=user,
                        role='pending'
                    )

                    messages.success(
                        request,
                        'Account created successfully! We are reviewing your '
                        'profile and will approve it shortly. Please check '
                        'back later to access your dashboard.'
                    )
                    return redirect('login')

            except Exception:
                # If anything goes wrong, show error message
                messages.error(
                    request,
                    'There was an error creating your account. '
                    'Please try again.'
                )
                # Re-display the form with errors

    else:
        form = CustomUserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
