from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def employee_dashboard(request):
    """Dashboard view for employees"""
    return render(request, 'core/employee_dashboard.html')
