"""
URL configuration for booking_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('login', permanent=False)),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include("core.urls"), name="core-urls"),
    path('admin/', admin.site.urls),
]
