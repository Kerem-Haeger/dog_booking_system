# Import all views for backward compatibility
from .client_views import client_dashboard, add_pet, book_appointment
from .employee_views import employee_dashboard
from .manager_views import (
    manager_dashboard, approve_pets, approve_appointments
)
from .api_views import fetch_available_slots, get_service_price
from .base import is_manager, is_client, is_employee

# Keep the redirect function in the main views.py for now
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from ..models import UserProfile


@login_required
def redirect_by_role(request):
    """Redirect users to appropriate dashboard based on their role"""
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')

    try:
        role = user.userprofile.role
    except UserProfile.DoesNotExist:
        return HttpResponse(
            "Error: This user does not have a UserProfile. "
            "Please create one via the admin site."
        )

    if role == 'client':
        return redirect('client_dashboard')
    elif role == 'employee':
        return redirect('employee_dashboard')
    elif role == 'manager':
        return redirect('manager_dashboard')
    else:
        return HttpResponse("Unknown role.")


# Export all functions for easy import
__all__ = [
    'redirect_by_role',
    'client_dashboard',
    'add_pet',
    'book_appointment',
    'employee_dashboard',
    'manager_dashboard',
    'approve_pets',
    'approve_appointments',
    'fetch_available_slots',
    'get_service_price',
    'is_manager',
    'is_client',
    'is_employee',
]
