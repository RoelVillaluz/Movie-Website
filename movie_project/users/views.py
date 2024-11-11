import random
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout as auth_logout
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from movies.forms import MovieSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, get_available_genres, filter_queryset, sort, toggle_upcoming
from users.models import CustomList, Follow, Profile, Watchlist
from .forms import CustomUserCreationForm, ListForm
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from movies.models import Award, Movie, MovieImage, User


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    model = Movie # only for getting random image 

    def get_success_url(self) -> str:
        return reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_images = MovieImage.objects.all()
                
        context.update({
            'movie_images': movie_images,
            'random_image': random.choice(movie_images)
        })

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
        movie_images = MovieImage.objects.all()

        context.update({
            'movie_images': movie_images,
            'random_image': random.choice(movie_images)
        })
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
        watchlist_movies = watchlist.movies.all().order_by('title')

        view_mode = request.GET.get('view', 'list')

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

        filters = Q()

        # Add genre filters 
        if selected_genres:
            genre_q = Q()
            for genre_name in selected_genres:
                genre_q |= Q(genres__name=genre_name)
            filters |= genre_q

        # Add award category filters 
        if selected_award_categories:
            award_q = Q()
            for award_category in selected_award_categories:
                award_q |= Q(awards__category=award_category, awards__winner=True)
            filters |= award_q

        # Add actor filters 
        if selected_actors:
            actor_q = Q()
            for actor in selected_actors:
                actor_q |= Q(actors__name=actor)
            filters |= actor_q

        # Apply the combined filters to the queryset
        if filters:
            watchlist_movies = watchlist_movies.filter(filters).distinct()

        # Get distinct award categories where the movie is a winner
        award_categories = Award.objects.filter(winner=True).values_list('category', flat=True).distinct()

        show_layout_buttons = True

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
            'upcoming': request.GET.get('upcoming', 'off'),
            'view_mode': view_mode,
            'show_layout_buttons': show_layout_buttons
        }
        return render(request, self.template_name, context)
    

class ProfileDetailView(DetailView):
    pass

@login_required(login_url='login')
def follow_content(request, model_name, object_id):
    content_type = get_object_or_404(ContentType, model=model_name)

    profile = get_object_or_404(Profile, user=request.user)

    follow = Follow.objects.filter(
        profile=profile,
        content_type=content_type,
        object_id=object_id,
    ).first()

    if follow:
        follow.delete()
        messages.success(request, f'You have unfollowed {follow.content_object}.')
    else:
        # Follow if the follow object does not exist
        follow = Follow.objects.create(
            profile=profile,
            content_type=content_type,
            object_id=object_id,
        )
        messages.success(request, f'You are now following {follow.content_object}.')

    return redirect(request.META.get('HTTP_REFERER', 'index'))


class CreateListView(CreateView):
    model = CustomList
    template_name = 'users/create-list.html'
    form_class = ListForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            movies = form.cleaned_data.get('movies')
            profile = Profile.objects.get(user=request.user)

            user_list = CustomList.objects.create(name=name, profile=profile)

            user_list.movies.set(movies)

            return redirect('index')
        
        return redirect('index')

    def get(self, request, *args, **kwargs):

        context = {
            'form': self.form_class()
        }

        return render(request, self.template_name, context)