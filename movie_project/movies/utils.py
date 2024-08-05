import random
import string
import requests
import os
from decouple import config

from movies.models import Movie, Review, User


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
    weights = [1, 1, 2, 2, 2, 2, 3, 4, 5, 5]  # Higher weights for 7, 8, 9, 10 and lower for 1, 2

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