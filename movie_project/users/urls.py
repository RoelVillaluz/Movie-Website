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
    path('lists/<int:pk>', views.CustomListDetailView.as_view(), name='list-detail')
]