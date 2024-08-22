from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail"),
    path("genres/", views.GenreListView.as_view(), name='genre-list'),
    path("genres/<int:pk>", views.GenreDetailView.as_view(), name='genre-detail'),
    path("actors/<int:pk>", views.ActorDetailView.as_view(), name='actor-detail'),
    path("directors/<int:pk>", views.DirectorDetailView.as_view(), name='director-detail'),
    path('add_to_watchlist/<int:id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('search_results/', views.SearchView.as_view(), name='search_results'),
]