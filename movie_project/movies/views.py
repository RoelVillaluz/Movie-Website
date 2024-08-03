from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from .models import Actor, Movie, Genre
from django.views.generic import ListView, DetailView
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Count

today = date.today()
one_month_before = today - relativedelta(months=1)

class IndexListView(ListView):
    model = Movie
    template_name = 'movies/index.html'
    context_object_name = 'movies'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Movie.objects.all()[:20]
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_movies'] = Movie.objects.filter(release_date__gte=one_month_before)
        context['popular_genres'] = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:3]
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

class GenreListView(ListView):
    model = Genre
    context_object_name = 'genres'
    template_name = 'movies/genre-list.html'

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
    
class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movies/actor-detail.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = self.object.movies.all()
        return context