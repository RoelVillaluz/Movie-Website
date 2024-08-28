from collections import defaultdict
from datetime import date
import math
import random
import string
from django.conf import settings
import requests
import os
from decouple import config
from moviepy.editor import VideoFileClip
from django.core.files import File
from movies.models import Actor, Award, Director, Movie, Review, User
from PIL import Image
from django.db.models import Avg, Count

from django.db.models import Avg, F
today = date.today()

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
        return queryset.annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews')).order_by('avg_rating', 'review_count')
    elif sort_by == 'rating_desc':
        return queryset.annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews')).order_by('-avg_rating', '-review_count')
    elif sort_by == 'runtime_asc':
        return queryset.order_by(F('hours') * 60 + F('minutes'))
    elif sort_by == 'runtime_desc':
        return queryset.order_by(-(F('hours') * 60 + F('minutes')))
    elif sort_by == 'popularity':
        return queryset.annotate(review_count=Count('reviews')).order_by('-review_count')
    return queryset

def available_genres(queryset):
    """Get only genres with movies for queryset"""
    genres_with_movies = defaultdict(list)
    for movie in queryset:
        for genre in movie.genres.all():
            genres_with_movies[genre.name].append(movie)

    genres_with_movies = dict(sorted(genres_with_movies.items()))

    return genres_with_movies

def available_award_categories(queryset):
    """ Get only award categories with movies for queryset """
    categories_with_movies = defaultdict(list)
    award_categories_with_winners = Award.objects.filter(movie__in=queryset, winner=True).values_list('category', flat=True).distinct()

    for movie in queryset:
        for award in movie.awards.filter(category__in=award_categories_with_winners):
            categories_with_movies[award.category].append(movie)

    categories_with_movies = sorted(dict(categories_with_movies))

    return categories_with_movies

def available_actors(queryset):
    """ Get only actors with movies for queryset """
    actors_in_queryset = defaultdict(list)
    for movie in queryset:
        for actor in movie.actors.all():
            actors_in_queryset[actor].append(movie)

    return actors_in_queryset

def filter_queryset(queryset, genre_name=None, award_category=None, actor=None):
    if genre_name:
        queryset = queryset.filter(genres__name=genre_name)
    if award_category:
        queryset = queryset.filter(awards__category=award_category)
    if actor:
        queryset = queryset.filter(actors__name=actor)
    return queryset


def toggle_upcoming(queryset):
    return queryset.filter(release_date__gt=today)


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

def get_actors_and_most_popular_movie(actors):
    actor_and_most_popular_movie = {}

    for actor in actors:
        most_popular_movie_of_actor = (
            actor.movies.annotate(review_count=Count('reviews'))
            .order_by('-review_count')
            .values_list('title', flat=True)
            .first()
        )
        if most_popular_movie_of_actor:
            actor_and_most_popular_movie[actor] = most_popular_movie_of_actor

    return actor_and_most_popular_movie


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
    ).order_by('-avg_rating', '-review_count').exclude(review_count__lt=5)[:num_of_movies]

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


def populate_user_review():
    users = User.objects.all()
    user = random.choice(users)

    movies = Movie.objects.all()        

    # Define adjectives for various review categories
    horrible_adjectives = ["terrible", "awful", "dreadful", "horrific", "atrocious", "abysmal", "painful", "disastrous", "unwatchable", "disgraceful"]
    mediocre_adjectives = ["average", "unremarkable", "mediocre", "so-so", "passable", "lackluster", "forgettable", "bland", "ordinary", "underwhelming"]
    good_adjectives = ["good", "decent", "enjoyable", "pleasant", "solid", "entertaining", "satisfying", "well-executed", "worthwhile", "pleasing"]
    amazing_adjectives = ["amazing", "captivating", "brilliant", "outstanding", "exceptional", "fantastic", "incredible", "remarkable", "spectacular", "impressive"]

    # Define review templates for each category
    horrible_templates = [
        lambda movie: f'I can barely recommend "{movie.title}". It was {random.choice(horrible_adjectives)} and left much to be desired.',
        lambda movie: f'"{movie.title}" was a letdown. The experience was {random.choice(horrible_adjectives)} and not worth your time.',
        lambda movie: f'Watching "{movie.title}" was a {random.choice(horrible_adjectives)} ordeal. I struggled to stay engaged.',
        lambda movie: f'Unfortunately, "{movie.title}" is a {random.choice(horrible_adjectives)} film that fails to deliver on any front.',
        lambda movie: f'"{movie.title}" was {random.choice(horrible_adjectives)}. Even the acting couldn’t save this disaster.'
    ]

    mediocre_templates = [
        lambda movie: f'"{movie.title}" was {random.choice(mediocre_adjectives)}—it didn’t blow me away, but it wasn’t terrible either.',
        lambda movie: f'I’d describe "{movie.title}" as {random.choice(mediocre_adjectives)}. It has its moments, but overall it’s quite average.',
        lambda movie: f'"{movie.title}" left me feeling {random.choice(mediocre_adjectives)}. It’s not a waste of time, but it’s not particularly memorable.',
        lambda movie: f'The film "{movie.title}" was {random.choice(mediocre_adjectives)} at best. There are better ways to spend your time.',
        lambda movie: f'"{movie.title}" is {random.choice(mediocre_adjectives)}—it’s an okay movie that lacks excitement.'
    ]

    good_templates = [
        lambda movie: f'I enjoyed "{movie.title}" quite a bit. It’s a {random.choice(good_adjectives)} film with some solid performances.',
        lambda movie: f'"{movie.title}" was a pleasant surprise. I found it to be {random.choice(good_adjectives)} and worth the watch.',
        lambda movie: f'"{movie.title}" delivers a {random.choice(good_adjectives)} experience. It’s not perfect, but it’s definitely enjoyable.',
        lambda movie: f'The film "{movie.title}" was {random.choice(good_adjectives)}—a nice mix of engaging plot and good acting.',
        lambda movie: f'Overall, "{movie.title}" was {random.choice(good_adjectives)}. It’s a decent choice for a movie night.'
    ]

    amazing_templates = [
        lambda movie: f'"{movie.title}" is nothing short of {random.choice(amazing_adjectives)}. It captivated me from start to finish.',
        lambda movie: f'Without a doubt, "{movie.title}" is an {random.choice(amazing_adjectives)} masterpiece. It exceeded all my expectations.',
        lambda movie: f'I was blown away by "{movie.title}". It’s a {random.choice(amazing_adjectives)} film that deserves high praise.',
        lambda movie: f'The film "{movie.title}" is a {random.choice(amazing_adjectives)} example of great cinema. It’s a must-watch.',
        lambda movie: f'"{movie.title}" was absolutely {random.choice(amazing_adjectives)}. The direction, acting, and story were all top-notch.'
    ]

    # Loop through each movie and create a review
    for movie in movies:
        rating = random.randint(1, 10)
        if rating <= 2:
            description = random.choice(horrible_templates)(movie)
        elif rating <= 4:
            description = random.choice(mediocre_templates)(movie)
        elif rating <= 7:
            description = random.choice(good_templates)(movie)
        else:
            description = random.choice(amazing_templates)(movie)

        Review.objects.create(
            user=user,
            movie=movie,
            description=description,
            rating=rating
        )

def populate_review_likes():
    users = User.objects.all()
    reviews = Review.objects.all()
    for user in users:
        review = random.choice(reviews)
        review.likes.add(user)