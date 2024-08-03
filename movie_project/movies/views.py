from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from .models import Actor, Movie, Genre
from django.views.generic import ListView, DetailView

class IndexListView(ListView):
    model = Movie
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Movie.objects.all()[:20]
        return queryset
    
    # Movie.objects.filter(release_date__gte='2024-1-1') for new movies later

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'movies/genre-movies.html'
    context_object_name = 'genre'

    def get_queryset(self):
        return Genre.objects.prefetch_related('movies')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = self.object.movies.all()
        return context
