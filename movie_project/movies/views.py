from collections import defaultdict
import random
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests

from movies.utils import create_users, get_genre_dict, get_popular_actors_and_movies, get_top_rated_movies, random_rating
from .models import Actor, Movie, Genre, Director, MovieVideo, Review, User
from django.views.generic import ListView, DetailView
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Avg
from django.views.generic.edit import FormView
from .forms import searchForm
import string

today = date.today()
one_month_before = today - relativedelta(months=1)


def index(request):
    # random_rating(30) # for populating reviews
    # create_users(10)  # for populating users

    movies = Movie.objects.all()
    popular_movies = movies.annotate(review_count=Count('reviews')).order_by('-review_count')[:20]
    new_movies = movies.filter(release_date__gte=one_month_before, release_date__lte=today)
    upcoming_movies = movies.filter(release_date__gt=today)
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]
    popular_actors_and_movie = get_popular_actors_and_movies()
    genre_dict = get_genre_dict(popular_genres)
    top_rated_movies = get_top_rated_movies(5)

    just_added = movies.order_by('-id')[:20]
    random_movie = random.choice(movies)

    context = {
        'movies': movies,
        'popular_movies': popular_movies,
        'new_movies': new_movies,
        'upcoming_movies': upcoming_movies,
        'popular_genres': popular_genres,
        'popular_actors_and_movie': popular_actors_and_movie,
        'genre_dict': genre_dict,
        'top_rated_movies': top_rated_movies,
        'just_added': just_added,
        'random_movie': random_movie,
    }

    return render(request, 'movies/index.html', context)

# Use the search view as is with a minor adjustment for consistency
class SearchView(FormView):
    template_name = 'movies/search-results.html'
    form_class = searchForm

    def form_valid(self, form):
        query = form.cleaned_data['query']
        movies = Movie.objects.filter(title__icontains=query)
        return self.render_to_response({'query': query, 'movies': movies})

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie-list.html'
    context_object_name = 'movies'
    form_class = searchForm

    def get_queryset(self):
        return Movie.objects.all().order_by('-id')

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        director = movie.directors.first()

        context.update({
            'director': director,
            'director_movies': director.movies.exclude(id=movie.id) if director else None,
            'overview_images': movie.images.all()[:2] if movie.images.count() >= 2 else None,
            'top_reviews': movie.reviews.order_by('-rating').exclude(description__isnull=True, description__exact='')[:2],
            'awards_by_name': self.get_awards_by_name(movie),
        })

        return context

    def get_awards_by_name(self, movie):
        awards_by_name = defaultdict(lambda: {'awards': [], 'win_count': 0, 'nomination_count': 0})
        for award in movie.awards.all():
            awards_by_name[award.award_name]['awards'].append(award)
            awards_by_name[award.award_name]['nomination_count'] += 1
            if award.winner:
                awards_by_name[award.award_name]['win_count'] += 1
        return dict(awards_by_name)

class GenreListView(ListView):
    model = Genre
    context_object_name = 'genres'
    template_name = 'movies/genre-list.html'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'movies/genre-movies.html'
    context_object_name = 'genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movies = self.object.movies.all()

        context.update({
            'movies': movies,
            'main_image': movies.first().backdrop_path.url if movies.exists() else None,
        })

        return context

class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movies/actor-detail.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actor = self.get_object()
        
        context.update({
            'movies': actor.movies.all(),
            'actor_rank': actor.get_rank(),
        })

        return context

class DirectorDetailView(DetailView):
    model = Director
    template_name = 'movies/director-detail.html'
    context_object_name = 'director'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        director = self.get_object()

        videos = [video for movie in director.movies.all() for video in movie.videos.all()]
        
        context.update({
            'known_for': director.movies.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4],
            'videos': videos,
            'main_video': videos[0] if videos else None,
            'awards': director.awards,
        })

        return context
