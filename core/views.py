from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def core_app(request):
    return HttpResponse("Welcome to our booking system!")
