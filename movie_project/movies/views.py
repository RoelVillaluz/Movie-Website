import random
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from .models import Actor, Movie, Genre, Director
from django.views.generic import ListView, DetailView
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Count

today = date.today()
one_month_before = today - relativedelta(months=1)
 
def index(request):
    movies = Movie.objects.all()[:20]
    new_movies = Movie.objects.filter(release_date__gte=one_month_before)
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]

    genre_dict = {}
    genre_set = set()

    for genre in popular_genres:
        movies_in_genre = genre.movies.exclude(pk__in=genre_set)
        random_movie = random.choice(movies_in_genre)
        genre_dict[genre.name] = [genre.name, random_movie.backdrop_path.url, genre.pk, random_movie.title]
        genre_set.add(random_movie.pk)

    return render(request, 'movies/index.html', {
        'movies': movies,
        'new_movies': new_movies,
        'popular_genres': popular_genres,
        'genre_dict': genre_dict
    })

# def search(request):
#     q = request.get('')
#     query = request.GET.get('q', '')
#     series = Series.objects.filter(title__icontains=q)
#     movies = Movie.objects.filter(title__icontains=q)


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        
        director = movie.directors.first()
        if director:
            director_movies = director.movies.exclude(id=movie.id)
            context['director_movies'] = director_movies
            
        return context

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