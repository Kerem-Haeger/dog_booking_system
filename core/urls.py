from django.urls import path
from . import views

urlpatterns = [
    path('redirect-by-role/', views.redirect_by_role, name='redirect_by_role'),
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('client/pets/add/', views.add_pet, name='add_pet'),
    path('client/appointments/book/', views.book_appointment, name='book_appointment'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/approve-appointments/', views.approve_appointments, name='approve_appointments'),
    path('manager/pets/pending/', views.approve_pets, name='approve_pets'),
]
