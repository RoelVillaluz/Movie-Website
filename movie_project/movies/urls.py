from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail"),
    path("movies/<int:pk>/images", views.MovieImagesView.as_view(), name="movie-images"),
    path('movies/edit_image/<int:id>/', views.EditMovieImageView.as_view(), name='edit-movie-image'),
    path("genres/", views.GenreListView.as_view(), name='genre-list'),
    path("genres/<int:pk>", views.GenreDetailView.as_view(), name='genre-detail'),
    path('people/<str:model_name>/<int:pk>/', views.PersonDetailView.as_view(), name='person-detail'),
    path("<str:model_name>/<int:pk>/images", views.PersonImagesView.as_view(), name='person-images'),
    path('people/<str:model_name>/edit_image/<int:pk>', views.EditPersonImageView.as_view(), name='edit-person-image'),
    path('delete_image/<int:id>', views.DeleteMovieImageView.as_view(), name='delete-image'),
    path('people/<str:model_name>/delete_image/<int:pk>', views.DeletePersonImageView.as_view(), name='delete-person-image'),
    path('add_to_watchlist/<int:id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('like_review/<int:id>/', views.like_review, name='like_review'), 
    path('search_results/', views.SearchView.as_view(), name='search_results'),
    path('search-suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('api/movie-images/', views.GetMovieImageDataView.as_view(), name='movie_images'),
]