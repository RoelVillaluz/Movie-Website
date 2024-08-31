import random
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout as auth_logout
from django.urls import reverse_lazy
from django.views import View

from movies.forms import MovieSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, get_available_genres, filter_queryset, sort, toggle_upcoming
from users.models import Profile, Watchlist
from .forms import CustomUserCreationForm
from django.views.generic import ListView, DetailView, CreateView
from movies.models import Award, Movie, MovieImage, User


movie_images = MovieImage.objects.all()
random_image1 = random.choice(movie_images)
random_image2 = random.choice(movie_images)

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    model = Movie # only for getting random image 

    def get_success_url(self) -> str:
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_image'] = random_image1
        return context
    
class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_image'] = random_image2
        return context

    
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")


class MyWatchlistView(View):
    model = Watchlist
    template_name = 'users/watchlist.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        watchlist = Watchlist.objects.get(user=user)
        watchlist_movies = watchlist.movies.all()

        # Search functionality
        search_form = SearchForm(request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            watchlist_movies = watchlist_movies.filter(title__icontains=query)

        # Calculate available genres and award categories with winners before applying filters
        genres_with_movies = get_available_genres(watchlist_movies)
        award_categories_with_winners = available_award_categories(watchlist_movies)
        actors_with_movies = available_actors(watchlist_movies)

        # Sorting logic
        sort_form = MovieSortForm(request.GET or None)
        if sort_form.is_valid():
            sort_by = sort_form.cleaned_data.get('sort_by')
            watchlist_movies = sort(watchlist_movies, sort_by)

        # Filtering logic
        selected_genres = request.GET.getlist('genre')
        selected_award_categories = request.GET.getlist('award_category')
        selected_actors = request.GET.getlist('actor')

        # Apply genre filters 
        for genre_name in selected_genres:
            watchlist_movies = filter_queryset(watchlist_movies, genre_name=genre_name)

        # Apply award category filters 
        for award_category in selected_award_categories:
            watchlist_movies = filter_queryset(watchlist_movies, award_category=award_category)

        # Apply actor filters 
        for actor in selected_actors:
            watchlist_movies = filter_queryset(watchlist_movies, actor=actor)

        # Toggle upcoming movies filter
        if request.GET.get('upcoming', 'off') == 'on':
            watchlist_movies = toggle_upcoming(watchlist_movies)

        # Get distinct award categories where the movie is a winner
        award_categories = Award.objects.filter(winner=True).values_list('category', flat=True).distinct()

        context = {
            'watchlist_movies': watchlist_movies,
            'search_form': search_form, 
            'sort_form': sort_form,
            'available_genres': genres_with_movies,  
            'award_categories_with_winners': award_categories_with_winners,
            'selected_genres': selected_genres,
            'award_categories': award_categories,
            'selected_award_categories': selected_award_categories,
            'actors_with_movies': actors_with_movies,
            'selected_actors': selected_actors,
            'upcoming': request.GET.get('upcoming', 'off')
        }
        return render(request, self.template_name, context)