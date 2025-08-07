from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import Service, PetProfile, ServicePrice
from ..utils import get_available_slots


@require_GET
def fetch_available_slots(request):
    """AJAX endpoint to fetch available appointment slots for a service"""
    service_id = request.GET.get('service_id')
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')

    if not service_id or not start_str or not end_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        service = Service.objects.get(id=service_id)
        start_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
    except (Service.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    all_slots = []
    date_range = (end_date - start_date).days + 1
    for date in (start_date + timedelta(n) for n in range(date_range)):
        time_strings = get_available_slots(service, date)
        for time_str in time_strings:
            start_dt = timezone.make_aware(
                datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            )
            end_dt = start_dt + service.duration
            all_slots.append({
                "title": "Available",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            })

    return JsonResponse(all_slots, safe=False)


@require_GET
def get_service_price(request):
    """AJAX endpoint to get service price for a specific pet size"""
    pet_id = request.GET.get('pet_id')
    service_id = request.GET.get('service_id')

    if not pet_id or not service_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        pet = PetProfile.objects.get(id=pet_id)
        service = Service.objects.get(id=service_id)
        price = service.get_price_for_size(pet.size)
        return JsonResponse({'price': f"{price:.2f}"})
    except (PetProfile.DoesNotExist, Service.DoesNotExist,
            ServicePrice.DoesNotExist):
        return JsonResponse({'error': 'Unable to calculate price'},
                            status=404)
