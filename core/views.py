from django.shortcuts import render
from django.views import generic
from .models import User, UserProfile

# Create your views here.
class UserList(generic.ListView):
    model = User
