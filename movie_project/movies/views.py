from django.http import JsonResponse
from django.shortcuts import render
import requests
from .models import Movie
from .utils import fetch_tmdb_data
from django.views.generic import ListView, DetailView



class IndexListView(ListView):
    model = Movie
    template_name = 'movies/index.html'
    context_object_name = 'movies'

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    
