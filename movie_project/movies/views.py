from collections import defaultdict
import random
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from movies.forms import MovieSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, available_genres, create_users, filter_queryset, get_genre_dict, get_popular_actors_and_movies, get_top_rated_movies, random_rating, sort
from users.models import Profile, Watchlist
from .models import Actor, Movie, Genre, Director, MovieVideo, Review, User
from django.views.generic import ListView, DetailView
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Avg


today = date.today()
one_month_before = today - relativedelta(months=1)

movies = Movie.objects.all()
actors = Actor.objects.all()

def index(request):
    # random_rating(30) # for populating reviews
    # create_users(10)  # for populating users
    popular_movies = movies.annotate(review_count=Count('reviews')).order_by('-review_count')[:20]
    new_movies = movies.filter(release_date__gte=one_month_before, release_date__lte=today)
    upcoming_movies = movies.filter(release_date__gt=today)
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]
    popular_actors_and_movie = get_popular_actors_and_movies()
    genre_dict = get_genre_dict(popular_genres)
    top_rated_movies = get_top_rated_movies(5)

    just_added = movies.order_by('-id').exclude(release_date__gt=today)[:20]
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

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie-list.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.all().order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movies = self.get_queryset()

        # Calculate available genres, actors, and award categories with winners before applying filters
        genres_with_movies = available_genres(movies)
        award_categories_with_winners = available_award_categories(movies)
        actors_with_movies = available_actors(movies)

        # Filtering logic
        selected_genres = self.request.GET.getlist('genre')
        selected_award_categories = self.request.GET.getlist('award_category')
        selected_actors = self.request.GET.getlist('actor')

        # Apply genre filters 
        for genre_name in selected_genres:
            movies = filter_queryset(movies, genre_name=genre_name)

        # Apply award category filters 
        for award_category in selected_award_categories:
            movies = filter_queryset(movies, award_category=award_category)

        # Apply actor filters 
        for actor in selected_actors:
            movies = filter_queryset(movies, actor=actor)

        # search form
        search_form = SearchForm(self.request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            movies = movies.filter(title__icontains=query)

        # Sorting logic using the request object
        sort_form = MovieSortForm(self.request.GET or None)
        if sort_form.is_valid():
            sort_by = sort_form.cleaned_data.get('sort_by')
            movies = sort(movies, sort_by)

        # Update context with the necessary data
        context.update({
            'movies': movies,  
            'available_genres': genres_with_movies,
            'award_categories_with_winners': award_categories_with_winners,
            'actors_with_movies': actors_with_movies,
            'selected_genres': selected_genres,
            'selected_award_categories': selected_award_categories,
            'selected_actors': selected_actors,
            'search_form': search_form,
            'sort_form': sort_form  
        })
        return context

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
        
@csrf_exempt
def add_to_watchlist(request, id):
    user = request.user
    movie = Movie.objects.get(id=id)
    
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Access the watchlist from the profile
    watchlist = profile.watchlist

    if movie not in watchlist.movies.all():
        watchlist.movies.add(movie)
        watchlisted = True
    else:
        watchlist.movies.remove(movie)
        watchlisted = False

    watchlist.save()

    return JsonResponse(
        {'watchlisted': watchlisted, 
         'movie_image': movie.poster_path.url})

class SearchView(View):
    form_class = SearchForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        query = ''
        movies = actors = directors = None
        selected_filter = request.GET.get('filter', 'all')  # Default to 'all' if no filter is provided
        
        if form.is_valid():
            query = form.cleaned_data.get('query', '')

            # Create a dictionary to map filters to their corresponding querysets
            filters = {
                'movies': Movie.objects.filter(title__icontains=query).order_by('title'),
                'actors': Actor.objects.filter(name__icontains=query).order_by('name'),
                'directors': Director.objects.filter(name__icontains=query).order_by('name')
            }

            # Apply the filter based on the selected filter type
            if selected_filter in filters:
                if selected_filter == 'movies':
                    movies = filters['movies']
                elif selected_filter == 'actors':
                    actors = filters['actors']
                elif selected_filter == 'directors':
                    directors = filters['directors']
            else:
                # If 'all' or an unknown filter is selected, retrieve all types
                movies = filters['movies']
                actors = filters['actors']
                directors = filters['directors']
        
        return render(request, 'movies/search_results.html', {
            'form': form,
            'movies': movies,
            'actors': actors,
            'directors': directors,
            'query': query,
            'selected_filter': selected_filter
        })