from .models import PetProfile, Appointment, UserProfile


def navigation_context(request):
    """
    Context processor to provide navigation-related data to all templates
    """
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        if request.user.userprofile.role == 'manager':
            # Add pending counts for manager notification badges
            context['pending_pets_count'] = PetProfile.objects.filter(
                profile_status='pending'
            ).count()
            context['pending_appointments_count'] = Appointment.objects.filter(
                status='pending'
            ).count()
            context['pending_users_count'] = UserProfile.objects.filter(
                role='pending'
            ).count()
    
    return context
