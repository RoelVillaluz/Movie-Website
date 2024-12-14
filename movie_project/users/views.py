import random
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout as auth_logout
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from movies.forms import MovieSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, get_available_genres, filter_queryset, sort, toggle_upcoming
from users.models import CustomList, Favorite, Follow, Profile, Watchlist
from .forms import CustomUserCreationForm, CustomListForm
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q, Avg
from movies.models import Award, Movie, MovieImage, Review, User


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
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        following_count = Follow.objects.filter(profile=profile).count() + profile.following.count()
        followers_count = Profile.objects.filter(following=profile).count()
        review_count = Review.objects.filter(user=profile.user).count()
        favorite_movies = Movie.objects.filter(reviews__user=profile.user).order_by('-reviews__rating')[:4]

        context = {
            'profile': profile,
            'following_count': following_count,
            'followers_count': followers_count,
            'review_count': review_count,
            'favorite_movies': favorite_movies
        }

        return render(request, self.template_name, context)

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
    form_class = CustomListForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            movies = form.cleaned_data.get('movies')
            privacy = request.POST.get('privacy')
            ranked_list = form.cleaned_data['ranked_list']
            profile = Profile.objects.get(user=request.user)

            user_list = CustomList.objects.create(name=name, 
                                                description=description, 
                                                privacy=privacy, 
                                                ranked_list=ranked_list, 
                                                profile=profile)

            user_list.movies.set(movies)

            return HttpResponseRedirect(reverse('list-detail', args=[user_list.pk]))
        
        return redirect('index')

    def get(self, request, *args, **kwargs):

        context = {
            'form': self.form_class(),
            'movies': Movie.objects.all()
        }

        return render(request, self.template_name, context)
    
class CustomListDetailView(DetailView):
    model = CustomList
    template_name = 'users/list-detail.html'
    context_object_name = 'list'

    def post(self, request, *args, **kwargs):
        custom_list = self.get_object()
        form = CustomListForm(request.POST, instance=custom_list)
        
        if 'save_name' in request.POST:
            if form.is_valid():
                custom_list = form.save(commit=False)
                custom_list.movies.set(custom_list.movies.all())  # Preserve movies relationship
                custom_list.description = request.POST.get('description', custom_list.description)
                custom_list.save()
                return redirect(request.META.get('HTTP_REFERER', 'index'))

        elif 'save_description' in request.POST:
            if form.is_valid():
                custom_list.description = request.POST.get('description', custom_list.description)
                custom_list.save()
                return redirect(request.META.get('HTTP_REFERER', 'index'))

        return redirect(request.META.get('HTTP_REFERER', 'index'))

    def get(self, request, **kwargs):
        custom_list = self.get_object()
        form = CustomListForm(instance=custom_list)
        custom_list_movies = custom_list.movies.all()

        genres_with_movies = get_available_genres(custom_list_movies)
        award_categories_with_winners = available_award_categories(custom_list_movies)
        actors_with_movies = available_actors(custom_list_movies)

        view_mode = request.GET.get('view', 'list')
        show_layout_buttons = True

        search_form = SearchForm(request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            custom_list_movies = custom_list_movies.filter(title__icontains=query)

        sort_form = MovieSortForm(request.GET or None)
        if sort_form.is_valid():
            sort_by = sort_form.cleaned_data.get('sort_by')
            custom_list_movies = sort(custom_list_movies, sort_by)

        selected_genres = request.GET.getlist('genre')
        selected_award_categories = request.GET.getlist('award_category')
        selected_actors = request.GET.getlist('actor')

        filters = Q()
        if selected_genres:
            genre_q = Q()
            for genre_name in selected_genres:
                genre_q |= Q(genres__name=genre_name)
            filters |= genre_q

        if selected_award_categories:
            award_q = Q()
            for award_category in selected_award_categories:
                award_q |= Q(awards__category=award_category, awards__winner=True)
            filters |= award_q

        if selected_actors:
            actor_q = Q()
            for actor in selected_actors:
                actor_q |= Q(actors__name=actor)
            filters |= actor_q

        if filters:
            custom_list_movies = custom_list.movies.filter(filters).distinct()

        award_categories = Award.objects.filter(winner=True).values_list('category', flat=True).distinct()

        context = {
            'custom_list': custom_list,
            'custom_list_movies': custom_list_movies,
            'view_mode': view_mode,
            'show_layout_buttons': show_layout_buttons,
            'search_form': search_form,
            'sort_form': sort_form,
            'available_genres': genres_with_movies,
            'award_categories_with_winners': award_categories_with_winners,
            'actors_with_movies': actors_with_movies,
            'selected_award_categories': selected_award_categories,
            'selected_genres': selected_genres,
            'selected_actors': selected_actors,
            'award_categories': award_categories,
            'form': form
        }

        return render(request, self.template_name, context)

@login_required(login_url='/login')
@csrf_exempt    
def add_to_watched_movies(request, id):
    user = request.user
    movie = Movie.objects.get(id=id)

    profile, created = Profile.objects.get_or_create(user=user)
    watchlist = profile.watchlist

    watchlisted = None

    if movie not in profile.watched_movies.all():
        profile.watched_movies.add(movie)
        if movie in watchlist.movies.all():
            watchlist.movies.remove(movie)
            watchlisted = False

        watched = True
    else:
        profile.watched_movies.remove(movie)
        watched = False

    return JsonResponse({
        'watched': watched,
        'watchlisted': watchlisted,
        'movie_image': movie.poster_path.url # for notification 
    })

@login_required(login_url='/login')
@csrf_exempt  
def add_to_favorites(request, model_name, object_id):
    user = request.user

    content_type = get_object_or_404(ContentType, model=model_name)

    profile, created = Profile.objects.get_or_create(user=user)

    movie = get_object_or_404(content_type.model_class(), id=object_id)

    favorite = Favorite.objects.filter(profile=profile, content_type=content_type, object_id=object_id)
    is_favorited = favorite.exists()

    if is_favorited:
        favorite.delete()
        favorited = False

    else:
        favorite = Favorite.objects.create(profile=profile, content_type=content_type, object_id=object_id)
        favorited = True
        
    return JsonResponse({
        'favorited': favorited,
        'image': movie.poster_path.url
    })