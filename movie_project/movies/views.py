from typing import Any
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import render
import requests
from .models import Movie
from .utils import fetch_tmdb_movies
from django.views.generic import ListView, DetailView



class IndexListView(ListView):
    model = Movie
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Movie.objects.all()[:20]
        return queryset

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    
