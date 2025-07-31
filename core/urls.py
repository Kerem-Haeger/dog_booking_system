from django.urls import path
from . import views

urlpatterns = [
    path('redirect-by-role/', views.redirect_by_role, name='redirect_by_role'),
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
]
