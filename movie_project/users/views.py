import random
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout as auth_logout
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.views.generic import ListView, DetailView, CreateView
from movies.models import Movie, MovieImage, User


movie_images = MovieImage.objects.all()
random_image = random.choice(movie_images)

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    model = Movie # only for getting random image 

    def get_success_url(self) -> str:
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_image'] = random_image
        return context
    
class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response
    
    
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")
