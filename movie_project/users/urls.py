from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path("logout", views.logout, name="logout"),
]