from collections import defaultdict
import random
import string
from django.conf import settings
import requests
import os
from decouple import config
from moviepy.editor import VideoFileClip
from django.core.files import File
from movies.models import Actor, Movie, Review, User
from PIL import Image
from django.db.models import Avg, Count

from django.db.models import Avg, F

movies = Movie.objects.all()

def sort(queryset, sort_by):
    if sort_by == 'title_asc':
        return queryset.order_by('title')
    elif sort_by == 'title_desc':
        return queryset.order_by('-title')
    elif sort_by == 'release_date_asc':
        return queryset.order_by('release_date')
    elif sort_by == 'release_date_desc':
        return queryset.order_by('-release_date')
    elif sort_by == 'rating_asc':
        return queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('avg_rating')
    elif sort_by == 'rating_desc':
        return queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort_by == 'runtime_asc':
        return queryset.order_by(F('hours') * 60 + F('minutes'))
    elif sort_by == 'runtime_desc':
        return queryset.order_by(-(F('hours') * 60 + F('minutes')))
    return queryset

def available_genres(queryset):
    genres_with_movies = defaultdict(list)
    for movie in queryset:
        for genre in movie.genres.all():
            genres_with_movies[genre.name].append(movie)

    return dict(genres_with_movies)


def get_popular_actors_and_movies():
    """Get popular actors and their most popular movie."""
    popular_actors_and_movie = defaultdict(list)
    popular_actors = Actor.objects.annotate(
        movie_review_count=Count('movies__reviews')
        ).order_by('-movie_review_count')[:5]

    for actor in popular_actors:
        most_popular_movie_of_actor = (
            actor.movies.annotate(review_count=Count('reviews'))
            .order_by('-review_count')
            .values_list('title', flat=True)
            .first()
        )
        if most_popular_movie_of_actor:
            popular_actors_and_movie[actor].append(most_popular_movie_of_actor)
    
    return dict(popular_actors_and_movie)

def get_genre_dict(popular_genres):
    """Get a dictionary of popular genres and a random movie for each genre."""
    genre_dict = {}
    genre_set = set()

    for genre in popular_genres:
        movies_in_genre = genre.movies.exclude(pk__in=genre_set)
        if movies_in_genre.exists():
            random_movie = random.choice(movies_in_genre)
            genre_dict[genre.name] = [
                genre.name, random_movie.backdrop_path.url, genre.pk, random_movie.title
            ]
            genre_set.add(random_movie.pk)

    return genre_dict

def get_top_rated_movies(num_of_movies):
    top_rated_movies = Movie.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-review_count').exclude(review_count__lt=3)[:num_of_movies]

    return top_rated_movies


# def fetch_tmdb_movies(endpoint, params):
#     api_token = config('API_TOKEN')
#     url = f"https://api.themoviedb.org/3/{endpoint}"
#     headers = {
#         "accept": "application/json",
#         "Authorization": f"Bearer {api_token}"
#     }
#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         return response.json().get('results', [])
#     else:
#         return []  

# # Example usage
# if __name__ == "__main__":
#     endpoint = "movie/popular"
#     params = {"language": "en-US", "page": 1}
#     data = fetch_tmdb_movies(endpoint, params)
#     print(data)

def random_rating(num_of_reviews):
    users = User.objects.all()
    movies = Movie.objects.all()

    # Define the ratings and their respective weights
    ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    weights = [1, 1, 1, 1, 2, 2, 2, 3, 4, 5]  # Higher weights for 7, 8, 9, 10 and lower for 1, 2

    for i in range(num_of_reviews):
        Review.objects.create(
            user=random.choice(users),
            movie=random.choice(movies),
            description=generate_random_string(255),
            rating=random.choices(ratings, weights=weights, k=1)[0],
        )

def create_users(num_users):
    for i in range(num_users):
        username = generate_random_string(8)
        password = generate_random_string(16)
        user = User.objects.create(username=username, password=password)
        user.save()

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))
