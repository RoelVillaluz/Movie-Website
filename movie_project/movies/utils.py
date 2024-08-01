import requests
import os
from decouple import config


def fetch_tmdb_movies(endpoint, params):
    api_token = config('API_TOKEN')
    url = f"https://api.themoviedb.org/3/{endpoint}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return []  

# Example usage
if __name__ == "__main__":
    endpoint = "movie/popular"
    params = {"language": "en-US", "page": 1}
    data = fetch_tmdb_movies(endpoint, params)
    print(data)