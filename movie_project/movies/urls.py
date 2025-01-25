from django.urls import path
from . import views

urlpatterns = [
    # General
    path("", views.index, name="index"),
    
    # Movies
    path("movies/", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail"),
    path("movies/<int:pk>/images", views.MovieImagesView.as_view(), name="movie-images"),
    path("movies/<int:pk>/reviews", views.MovieReviewListView.as_view(), name="movie-reviews"),
    path("movies/edit_image/<int:id>", views.EditMovieImageView.as_view(), name="edit-movie-image"),
    path("movies/delete_image/<int:id>", views.DeleteMovieImageView.as_view(), name="delete-image"),

    # Custom Lists
    path('lists/', views.CustomListListView.as_view(), name="all-custom-lists"),
    
    # Genres
    path("genres/", views.GenreListView.as_view(), name="genre-list"),
    path("genres/<int:pk>", views.GenreDetailView.as_view(), name="genre-detail"),
    
    # People
    path("people/<str:model_name>/<int:pk>/", views.PersonDetailView.as_view(), name="person-detail"),
    path("people/<str:model_name>/<int:pk>/images", views.PersonImagesView.as_view(), name="person-images"),
    path("people/<str:model_name>/edit_image/<int:pk>", views.EditPersonImageView.as_view(), name="edit-person-image"),
    path("people/<str:model_name>/delete_image/<int:pk>", views.DeletePersonImageView.as_view(), name="delete-person-image"),
    
    # Watchlist
    path("add_to_watchlist/<int:id>/", views.add_to_watchlist, name="add_to_watchlist"),
    
    # Reviews
    path("add_review/<int:id>/", views.add_review, name="add_review"),
    path("like_review/<int:id>/", views.like_review, name="like_review"),
    
    # Search
    path("search_results/", views.SearchView.as_view(), name="search_results"),
    path("search-suggestions/", views.SearchSuggestionsView.as_view(), name="search_suggestions"),
    
    # API
    path("api/movie-images/", views.GetMovieImageDataView.as_view(), name="movie_images"),
]
