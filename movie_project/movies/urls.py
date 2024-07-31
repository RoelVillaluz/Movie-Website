from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexListView.as_view(), name="index"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail")
]