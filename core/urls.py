from django.urls import path
from . import views
from .views import fetch_available_slots
from .views.api_views import (
     get_service_price, get_calendar_events, debug_appointments,
     approve_appointment_ajax, reject_appointment_ajax,
     get_available_employees, reassign_appointment_ajax
)

urlpatterns = [
     path('redirect-by-role/', views.redirect_by_role,
          name='redirect_by_role'),
     path('client/', views.client_dashboard, name='client_dashboard'),
     path('client/pets/add/', views.add_pet, name='add_pet'),
     path('client/appointments/book/', views.book_appointment,
          name='book_appointment'),
     path('client/appointments/cancel/<int:appointment_id>/',
          views.cancel_appointment, name='cancel_appointment'),
     path('ajax/available-slots/', fetch_available_slots,
          name='fetch_available_slots'),
     path('employee/', views.employee_dashboard, name='employee_dashboard'),
     path('manager/', views.manager_dashboard, name='manager_dashboard'),
     path('manager/approve-appointments/', views.approve_appointments,
          name='approve_appointments'),
     path('manager/pets/pending/', views.approve_pets, name='approve_pets'),
     path('ajax/get-service-price/', get_service_price,
          name='get_service_price'),
     path('ajax/calendar-events/', get_calendar_events,
          name='get_calendar_events'),
     path('ajax/debug-appointments/', debug_appointments,
          name='debug_appointments'),
     path('ajax/approve-appointment/', approve_appointment_ajax,
          name='approve_appointment_ajax'),
     path('ajax/reject-appointment/', reject_appointment_ajax,
          name='reject_appointment_ajax'),
     path('ajax/get-available-employees/', get_available_employees,
          name='get_available_employees'),
     path('ajax/reassign-appointment/', reassign_appointment_ajax,
          name='reassign_appointment_ajax'),
]
