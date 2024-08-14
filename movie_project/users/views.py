from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, logout as auth_logout
from django.urls import reverse_lazy
from . import forms
from django.views.generic import ListView, DetailView


from movies.models import Movie, User

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    model = Movie

    def get_success_url(self) -> str:
        return reverse_lazy('index')
    
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")
