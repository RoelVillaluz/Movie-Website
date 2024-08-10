from collections import defaultdict
import random
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests

from movies.utils import create_users, random_rating
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
    # create_users(10) # for populating users
    movies = Movie.objects.all()

    popular_movies = movies[:20]
    new_movies = Movie.objects.filter(release_date__gte=one_month_before)
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]

    genre_dict = {}
    genre_set = set()

    for genre in popular_genres:
        movies_in_genre = genre.movies.exclude(pk__in=genre_set)
        random_movie = random.choice(movies_in_genre)
        genre_dict[genre.name] = [genre.name, random_movie.backdrop_path.url, genre.pk, random_movie.title]
        genre_set.add(random_movie.pk)

    top_rated_movies = Movie.objects.annotate(avg_rating=Avg('reviews__rating'), 
                                              review_count=Count('reviews')
                                              ).order_by('-avg_rating', '-review_count'
                                              ).exclude(review_count__lt=3)[:5]
    
    just_added = movies.order_by('-id')[:20]

    return render(request, 'movies/index.html', {
        'movies': movies,
        'popular_movies': popular_movies,
        'new_movies': new_movies,
        'popular_genres': popular_genres,
        'genre_dict': genre_dict,
        'top_rated_movies': top_rated_movies,
        'just_added': just_added
    })

# def search(request):
#     q = request.get('')
#     query = request.GET.get('q', '')
#     series = Series.objects.filter(title__icontains=q)
#     movies = Movie.objects.filter(title__icontains=q)

class searchView(FormView):
    template_name = 'movies/search-results.html'
    form_class = searchForm

    def form_valid(self, form):
        query = form.cleaned_data['query']
        movies = Movie.objects.filter(title__icontains=query)
        # series = Series.objects.filter(title__icontains=query)

        context = {
            'query' : query,
            'movies': movies
        }

        return self.render_to_response(context)
    
class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie-list.html'
    context_object_name = 'movies'
    form_class = searchForm

    def get_queryset(self):
        queryset = Movie.objects.all().order_by('-id')
        return queryset

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        
        director = movie.directors.first()
        context['director'] = director
        
        if director:
            director_movies = director.movies.exclude(id=movie.id)
            if director_movies.exists():
                context['director_movies'] = director_movies

        movie_images = movie.images.all()

        if len(movie_images) >= 2:
            context['overview_images'] = movie_images[:2]

        context['top_reviews'] = movie.reviews.order_by('-rating').exclude(description__isnull=True).exclude(description__exact='')[:2]
            
        # Group awards by name
        awards_by_name = defaultdict(lambda: {'awards': [], 'win_count': 0, 'nomination_count': 0})
        for award in movie.awards.all():  
            award_name = award.award_name
            awards_by_name[award_name]['awards'].append(award)
            
            awards_by_name[award_name]['nomination_count'] += 1
            if award.winner:
                awards_by_name[award_name]['win_count'] += 1
        
        context['awards_by_name'] = dict(awards_by_name)

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

        movies = self.object.movies.all()
        context['movies'] = movies
        context['main_image'] = movies.first().backdrop_path.url
        return context
    
class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movies/actor-detail.html'
    context_object_name = 'actor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actor = self.get_object()
        context['movies'] = actor.movies.all()
        context['actor_rank'] = actor.get_rank()
        return context
    
class DirectorDetailView(DetailView):
    model = Director
    template_name = 'movies/director-detail.html'
    context_object_name = 'director'

    def get_context_data(self, **kwargs: Any):
        director = self.get_object()
        context = super().get_context_data(**kwargs)
        
        context['known_for'] = director.movies.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4]
        
        videos = [video for movie in director.movies.all() for video in movie.videos.all()]
        context['videos'] = videos
        context['main_video'] = videos[0] if videos else None

        return context