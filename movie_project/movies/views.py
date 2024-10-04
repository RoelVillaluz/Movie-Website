from collections import OrderedDict, defaultdict
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
from movies.utils import available_actors, available_award_categories, get_actor_accolades, get_available_genres, filter_queryset, get_actors_and_most_popular_movies, get_directors_and_most_popular_movies, get_genre_dict, get_movies_by_month_and_year, get_movies_by_year, get_popular_actors_and_movies, get_top_rated_movies, often_works_with, sort
from users.models import Follow, Profile, Watchlist
from .models import Actor, Movie, Genre, Director, MovieVideo, Review, User
from django.views.generic import ListView, DetailView
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Avg, Prefetch, Q
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile

today = date.today()
one_month_before = today - relativedelta(months=1)

def index(request):
    movies = Movie.objects.all()
    # random_rating(30) # for populating reviews
    # create_users(10)  # for populating users
    popular_movies = movies.annotate(review_count=Count('reviews')).order_by('-review_count')[:20]
    new_movies = movies.filter(release_date__gte=one_month_before, release_date__lte=today)
    upcoming_movies = movies.filter(release_date__gt=today).order_by('release_date')
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]
    popular_actors_and_movie = get_popular_actors_and_movies()
    genre_dict = get_genre_dict(popular_genres)
    top_rated_movies = get_top_rated_movies(5)

    most_popular_reviews = Review.objects.annotate(like_count=Count('likes')).order_by('-like_count').exclude(like_count__lt=1)[:2]

    just_added = movies.order_by('-id').exclude(release_date__gt=today)[:20]
    random_movie = random.choice(movies)

    upcoming_movie_and_date = get_movies_by_month_and_year(upcoming_movies, limit=2)

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
        'most_popular_reviews': most_popular_reviews,
        'upcoming_movie_and_date': upcoming_movie_and_date
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
        genres_with_movies = get_available_genres(movies)
        award_categories_with_winners = available_award_categories(movies)
        actors_with_movies = available_actors(movies)

        # Filtering logic
        selected_genres = self.request.GET.getlist('genre')
        selected_award_categories = self.request.GET.getlist('award_category')
        selected_actors = self.request.GET.getlist('actor')

        filters = Q()

        # Add genre filters 
        if selected_genres:
            genre_q = Q()
            for genre_name in selected_genres:
                genre_q |= Q(genres__name=genre_name)
            filters |= genre_q

        # Add award category filters 
        if selected_award_categories:
            award_q = Q()
            for award_category in selected_award_categories:
                award_q |= Q(awards__category=award_category)
            filters |= award_q

        # Add actor filters 
        if selected_actors:
            actor_q = Q()
            for actor in selected_actors:
                actor_q |= Q(actors__name=actor)
            filters |= actor_q

        # Apply the combined filters to the queryset
        if filters:
            movies = movies.filter(filters)

        # Search form
        search_form = SearchForm(self.request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            movies = movies.filter(title__icontains=query)

        # Sorting logic using the request object
        sort_form = MovieSortForm(self.request.GET or None)
        if sort_form.is_valid():
            sort_by = sort_form.cleaned_data.get('sort_by')
            movies = sort(movies, sort_by)

        movies = movies.distinct()

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
            'sort_form': sort_form,
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
            'top_reviews': movie.reviews.order_by('-rating')[:2],
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

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        first_letter_and_genre = defaultdict(list)
        genre_set = set()
        genres = Genre.objects.all()


        # get random movie images for genre page header
        movies = Movie.objects.exclude(release_date__gt=today)
        random_images = random.sample(list(movies), 5)

        # dictionary for first letters and genre 
        for genre in genres:
            movies_in_genre = genre.movies.exclude(pk__in=genre_set)
            if movies_in_genre.exists():
                first_letter = genre.name[0].upper()
                random_movie = random.choice(movies_in_genre)
                genre_info = [genre.name, random_movie.backdrop_path.url, genre.pk, genre.movies.count]
                first_letter_and_genre[first_letter].append(genre_info)
                genre_set.add(random_movie.pk)

        first_letter_and_genre = OrderedDict(sorted(first_letter_and_genre.items()))

        context.update({
            'random_images': random_images,
            'first_letter_and_genre': first_letter_and_genre
        })

        return context

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
        most_popular_movie = actor.most_popular_movie
        co_workers = often_works_with(actor)
        accolades = get_actor_accolades(actor)
        movies_by_year = get_movies_by_year(actor.movies.all().order_by('-release_date__year'))

        # Get logged-in user's profile and check if they follow this actor
        profile = Profile.objects.get(user=self.request.user) if self.request.user.is_authenticated else None
        is_following = Follow.objects.filter(
            profile=profile,
            content_type=ContentType.objects.get_for_model(actor),
            object_id=actor.id
        ).exists() if profile else False

        known_for = actor.movies.annotate(
                    review_count=Count('reviews')
                ).order_by('-review_count')[:4]

        context.update({
            'movies': actor.movies.all(),
            'actor_rank': actor.get_rank(),
            'avg_movie_rating': actor.movies.aggregate(Avg('reviews__rating')),
            'most_popular_movie': most_popular_movie,
            'follower_count': actor.follower_count,
            'age': actor.get_age,
            'default_bio': actor.default_bio,
            'co_workers': co_workers,
            'accolades': accolades,
            'is_following': is_following,
            'movies_by_year': movies_by_year,
            'known_for': known_for
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

def like_review(request, id):
    user = request.user
    review = get_object_or_404(Review, id=id)

    if user in review.likes.all():
        review.likes.remove(user)
        liked = False
    else:
        review.likes.add(user)
        liked = True
    
    like_count = review.likes.count()

    return JsonResponse({
        'liked': liked,
        'like_count': like_count
    })

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
            'selected_filter': selected_filter,
        })
    

class SearchSuggestionsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')

        movie_results = []
        actor_results = []
        director_results = []

        if query:
            # Get all matching movies without limiting the results
            all_matching_movies = Movie.objects.filter(title__icontains=query).prefetch_related(
                Prefetch('genres', queryset=Genre.objects.all())
            )

            # Get the first 3 matching movies
            movie_suggestions = all_matching_movies[:2]

            all_matching_actors = Actor.objects.filter(name__icontains=query)
            actor_suggestions = all_matching_actors[:2]

            all_matching_directors = Director.objects.filter(name__icontains=query)
            director_suggestions = all_matching_directors[:1]  

            for movie in movie_suggestions:
                # Get all genres for the movie
                all_genres = [genre.name for genre in movie.genres.all()]
                avg_rating = movie.avg_rating()
                # Choose only the first genre
                genre = all_genres[0] if all_genres else 'None'

                movie_results.append({
                    'id': movie.id,
                    'title': movie.title,
                    'avg_rating': avg_rating,
                    'year': movie.release_date.year,
                    'poster_path': movie.poster_path.url,
                    'genre': genre  
                })

            # Get actor suggestions and their most popular movie
            actor_and_most_popular_movie = get_actors_and_most_popular_movies(actor_suggestions, 1)

            actor_results = [{
                'id': actor.id,
                'name': actor.name,
                'image': actor.image.url,
                'most_popular_movie': actor_movie,
            } for actor, actor_movie in actor_and_most_popular_movie.items()]

            director_and_most_popular_movie = get_directors_and_most_popular_movies(director_suggestions, 1)

            # Get director suggestions
            director_results = [{
                'id': director.id,
                'name': director.name,
                'image': director.image.url,
                'most_popular_movie': director_movie,
            } for director, director_movie in director_and_most_popular_movie.items()]

        # Calculate the total number of matching searches
        total_matching_movies = all_matching_movies.count()
        total_matching_actors = all_matching_actors.count()
        total_matching_directors = all_matching_directors.count()

        return JsonResponse({
            'movies': movie_results,
            'movie_count': total_matching_movies,  
            'actors': actor_results,
            'actor_count': total_matching_actors,
            'directors': director_results,
            'director_count': total_matching_directors
        })
