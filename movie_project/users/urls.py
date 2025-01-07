from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path("logout", views.logout, name="logout"),
    path("watchlist/", views.MyWatchlistView.as_view(), name='watchlist'),
    path('profile/<int:pk>', views.ProfileDetailView.as_view(), name="profile"),
    path('follow/<str:model_name>/<int:object_id>/', views.follow_content, name='follow_content'),
    path('create_list', views.CreateListView.as_view(), name='create-list'),
    path('lists/<int:pk>', views.CustomListDetailView.as_view(), name='list-detail'),
    path('add_to_watched_movies/<int:id>/', views.add_to_watched_movies, name='add_to_watched_movies'),
    path('add_to_favorites/<str:model_name>/<int:object_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('add_to_list/<int:custom_list_id>/<int:movie_id>/', views.add_to_list, name="add_to_list"),
]

htmx_urlpatterns = [
    path('check_username/', views.check_username, name="check_username"),
    path('edit_profile_image', views.edit_profile_image, name="edit_profile_image"),
    path('edit_custom_list/<int:id>/', views.edit_custom_list, name="edit_custom_list"),
]

urlpatterns += htmx_urlpatterns