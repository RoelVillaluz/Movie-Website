from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail"),
    path("genres/", views.GenreListView.as_view(), name='genre-list'),
    path("genres/<int:pk>", views.GenreDetailView.as_view(), name='genre-detail'),
    path("actors/<int:pk>", views.ActorDetailView.as_view(), name='actor-detail'),
    path("<str:model_name>/<int:pk>/images", views.PersonImagesView.as_view(), name='person-images'),
    path("directors/<int:pk>", views.DirectorDetailView.as_view(), name='director-detail'),
    path('add_to_watchlist/<int:id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('like_review/<int:id>/', views.like_review, name='like_review'),
    path('search_results/', views.SearchView.as_view(), name='search_results'),
    path('search-suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('api/movie-images/', views.GetMovieImageDataView.as_view(), name='movie_images'),
    path('add_movie_images/', views.add_movie_images, name='add_movie_images'),
    
]