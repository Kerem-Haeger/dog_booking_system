from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import UserProfile, PetProfile


@login_required
def redirect_by_role(request):
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')

    try:
        role = user.userprofile.role
    except UserProfile.DoesNotExist:
        return HttpResponse(
            "Error: This user does not have a UserProfile."
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


@login_required
def client_dashboard(request):
    pets = PetProfile.objects.filter(user=request.user)
    return render(request, 'core/client_dashboard.html', {
        'pets': pets
    })


@login_required
def employee_dashboard(request):
    return render(request, 'core/employee_dashboard.html')


@login_required
def manager_dashboard(request):
    return render(request, 'core/manager_dashboard.html')
