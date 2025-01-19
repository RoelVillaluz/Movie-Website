from collections import defaultdict
from datetime import date, datetime
import math
import random
import string
from tempfile import NamedTemporaryFile
from django.conf import settings
from dotenv import load_dotenv
import requests
import os
from decouple import config
from django.core.files import File
from movies.models import Actor, Award, Director, Genre, Movie, Review, User
from PIL import Image
from django.db.models import Avg, Count, F
from django.contrib.contenttypes.models import ContentType
from itertools import islice
from django.db.models import Count, Q, F
from django.db.models.functions import Length
import difflib

from users.models import Follow, Profile

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
#     endpoint = "movie/upcoming"
#     params = {"language": "en-US", "page": 1}
#     data = fetch_tmdb_movies(endpoint, params)
#     print(data)

def create_movie_from_api():
    # Define the API URL and headers using the API key from the .env file
    url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer "
    }

    # Make the API request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        movies = data.get("results", [])

        for movie_data in movies:
            # Create the movie object and populate fields
            title = movie_data.get("title")
            overview = movie_data.get("overview", "No overview yet")
            release_date = movie_data.get("release_date")
            poster_path = movie_data.get("poster_path")
            backdrop_path = movie_data.get("backdrop_path")

            # Convert release_date to Date format
            if release_date:
                release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

            # Use the original resolution for images
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else None
            backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else None

            # Handle image files
            poster_file = None
            backdrop_file = None

            if poster_url:
                poster_file = download_image(poster_url)

            if backdrop_url:
                backdrop_file = download_image(backdrop_url)

            # Create movie instance
            movie = Movie(
                title=title,
                overview=overview,
                release_date=release_date,
                poster_path=poster_file,
                backdrop_path=backdrop_file
            )
            movie.save()

def download_image(url):
    """Download an image from the provided URL and return a Django File object."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create a temporary file to save the image
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()

            # Return a Django File object
            return File(img_temp, name=os.path.basename(url))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None

def sort(queryset, sort_by):
    """ Helper function for sorting movies """
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

def sort_reviews(queryset, sort_by):
    """ Helper function for sorting reviews """
    if sort_by == 'created_on_asc':
        return queryset.order_by('created_on')
    elif sort_by == 'created_on_desc':
        return queryset.order_by('-created_on')
    elif sort_by == 'popularity':
        return queryset.annotate(like_count=Count('likes')).order_by('-like_count')
    elif sort_by == 'rating_desc':
        return queryset.order_by('-rating')
    elif sort_by == 'rating_asc':
        return queryset.order_by('rating')
    elif sort_by == 'description_length_desc':
        return queryset.annotate(length=Length('description')).order_by('-length')
    elif sort_by == 'description_length_asc':
        return queryset.annotate(length=Length('description')).order_by('length')
    return queryset

def get_available_genres(queryset):
    """Get only genres with movies for queryset"""
    genres_with_movies = defaultdict(list)

    queryset = queryset.prefetch_related('genres')

    for movie in queryset:
        for genre in movie.genres.all():
            genres_with_movies[genre.name].append(movie)

    genres_with_movies = dict(sorted(genres_with_movies.items()))

    return genres_with_movies

def available_award_categories(queryset):
    """ Get only award categories with movies for queryset """
    categories_with_movies = defaultdict(list)
    award_categories_with_winners = Award.objects.filter(movie__in=queryset, winner=True).values_list('category', flat=True).distinct()

    queryset = queryset.prefetch_related('awards')
    
    for movie in queryset:
        for award in movie.awards.filter(category__in=award_categories_with_winners):
            categories_with_movies[award.category].append(movie)

    return sorted(dict(categories_with_movies))

def available_actors(queryset):
    """ Get only actors with movies for queryset """
    actors_in_queryset = defaultdict(list)

    queryset = queryset.prefetch_related('actors')

    for movie in queryset:
        for actor in movie.actors.all():
            actors_in_queryset[actor].append(movie)

    actors_in_queryset = dict(sorted(actors_in_queryset.items(), key=lambda x: x[0].name))    

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
    today = date.today()
    return queryset.filter(release_date__gt=today)


# def toggle_watched(queryset):
#     return queryset.filter(movie__in=user.profile.watched_movies)


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

def get_actors_and_most_popular_movies(actors, num_movies):
    """ returns a dictionary where the keys are actor objects and the values are lists of movie titles,
    ordered by the number of reviews in descending order. """
    
    actor_and_most_popular_movies = {}

    for actor in actors:
        most_popular_movies_of_actor = (
            actor.movies.annotate(review_count=Count('reviews'))
            .order_by('-review_count')
            .values_list('title', flat=True)[:num_movies]
        )
        if most_popular_movies_of_actor:
            actor_and_most_popular_movies[actor] = list(most_popular_movies_of_actor)

    return actor_and_most_popular_movies

def get_directors_and_most_popular_movies(directors, num_movies):
    """ returns a dictionary where the keys are actor objects and the values are lists of movie titles,
    ordered by the number of reviews in descending order. """
    
    director_and_most_popular_movies = {}

    for director in directors:
        most_popular_movies_of_director = (
            director.movies.annotate(review_count=Count('reviews'))
            .order_by('-review_count')
            .values_list('title', flat=True)[:num_movies]
        )
        if most_popular_movies_of_director:
            director_and_most_popular_movies[director] = list(most_popular_movies_of_director)

    return director_and_most_popular_movies

def get_genre_dict(genres):
    """Get a dictionary of popular genres and a random movie for each genre."""
    genre_dict = {}
    genre_set = set()

    for genre in genres:
        movies_in_genre = genre.movies.exclude(pk__in=genre_set)
        if movies_in_genre.exists():
            random_movie = random.choice(movies_in_genre)
            genre_dict[genre.name] = [
                genre.name, random_movie.backdrop_path.url, genre.pk, random_movie.title
            ]
            genre_set.add(random_movie.pk)

    sorted_genre_dict = dict(sorted(genre_dict.items()))

    return sorted_genre_dict

def get_top_rated_movies(num_of_movies):
    top_rated_movies = Movie.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-review_count').exclude(review_count__lt=4)[:num_of_movies]

    return top_rated_movies

def get_person_accolades(person):
    # Dictionary structure: {award_name: {category: {'wins': 0, 'nominations': 0}}}
    person_accolades = defaultdict(lambda: {'awards': [], 'win_count': 0, 'nomination_count': 0})

    awards = person.awards.all()

    for award in awards:
        person_accolades[award.award_name]['awards'].append(award)
        person_accolades[award.award_name]['nomination_count'] += 1
        if award.winner:
            person_accolades[award.award_name]['win_count'] += 1

    return dict(person_accolades)

def often_works_with(person):
    movies = person.movies.prefetch_related('actors', 'directors').all()  # Prefetch actors and directors for all movies
    co_workers = defaultdict(lambda: {'count': 0, 'name': '', 'image': '', 'type': ''})
    counted_co_workers = set()
    
    for movie in movies:
        # Create a combined list of all co-workers (actors and directors) excluding the person
        all_co_workers = [
            (co_worker, 'actor') for co_worker in movie.actors.exclude(id=person.id)
        ] + [
            (co_worker, 'director') for co_worker in movie.directors.exclude(id=person.id)
        ]

        # Use a set to track counted co-workers for this movie
        counted_co_workers = set()

        for co_worker, co_worker_type in all_co_workers:
            if co_worker.id not in counted_co_workers:
                co_workers[co_worker.id]['count'] += 1
                co_workers[co_worker.id]['name'] = co_worker.name
                co_workers[co_worker.id]['image'] = co_worker.image.url
                co_workers[co_worker.id]['type'] = co_worker_type
                counted_co_workers.add(co_worker.id)
    
    # Sort by count and limit to top 5 actors
    co_workers = sorted(co_workers.items(), key=lambda x: x[1]['count'], reverse=True)[:2]

    return co_workers

def convert_height_to_feet(person):
    if person.height != 0:
        height_in_feet = person.height / 30.48
        feet = int(height_in_feet)
        inches = round((height_in_feet - feet) * 12)
    else:
        return "N/A"
    
    return f"{feet}'{inches} ft"

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

def populate_follows_for_random_profiles(num_profiles=5):
    """
    Function to populate the Follow model with random profiles following random objects 
    of type Profile, Actor, or Director.
    
    Parameters:
    - num_profiles: the number of random profiles to follow objects (default: 5)
    """
    # Define the valid content types and their corresponding model classes
    valid_models = {
        Profile: ContentType.objects.get_for_model(Profile),
        Actor: ContentType.objects.get_for_model(Actor),
        Director: ContentType.objects.get_for_model(Director),
    }

    # Get random profiles
    random_profiles = Profile.objects.order_by('?')[:num_profiles]

    for profile in random_profiles:
        # Randomly select a model and its corresponding content type
        model_class = random.choice(list(valid_models.keys()))
        content_type = valid_models[model_class]

        # Get a random instance of the selected model class
        random_instance = model_class.objects.order_by('?').first()  # Get a random instance

        if random_instance:
            # Create follow entry for the selected profile and instance
            follow, created = Follow.objects.get_or_create(
                profile=profile,
                content_type=content_type,
                object_id=random_instance.id,
                defaults={'content_object': random_instance}
            )
            if created:
                print(f'{profile.user.username} now follows {random_instance}')
            else:
                print(f'{profile.user.username} already follows {random_instance}')
        else:
            print(f'No instances found for {model_class.__name__}')

def get_movies_by_year(queryset):
    movies_by_year = defaultdict(list)

    for movie in queryset:
        movies_by_year[movie.release_date.year].append(movie)

    return dict(movies_by_year)

def get_movies_by_month_and_year(queryset, limit=None):
    movies_by_month_and_year = defaultdict(list)

    for movie in queryset:
        release_month_year = movie.release_date.strftime('%B %Y')  # e.g., "September 2024"
        day = movie.release_date.strftime('%d')

        # Append a dictionary with movie and month_and_day
        if len(movies_by_month_and_year[release_month_year]) < 3:
            movies_by_month_and_year[release_month_year].append({
            'movie': movie,
            'day': day
        })

    if limit:
        return dict(islice(movies_by_month_and_year.items(), limit))

    return dict(movies_by_month_and_year)

def get_similar_movies(movie):
    """Gets similar movies based on mutual genres and checks if their name is similar."""

    # Step 1: Find movies with the same genres and exclude the current movie and then order by number of matching genres    
    similar_movies = Movie.objects.filter(genres__in=movie.genres.all()) \
                                  .exclude(id=movie.id)                  \
                                  .annotate(genre_count=Count('genres')) \
                                  .order_by('-genre_count')

    # Step 2: Sort the similar movies by title similarity (using substring matching)
    def title_similarity(m):
        """Simple function to return a measure of name similarity based on substring occurrence."""
        words_to_ignore = ['the', 'of', 'as', 'in']

        title = m.title.lower()
        movie_title = movie.title.lower()
        return sum(1 for word in movie_title.split() if word in title and word not in words_to_ignore)

    # Step 3: Sort by title similarity (most important) and genre count (secondary)
    similar_movies = sorted(similar_movies, key=lambda m: (title_similarity(m), m.genre_count), reverse=True)

    # Step 4: Limit to the top 5 most similar movies
    return similar_movies[:5]

