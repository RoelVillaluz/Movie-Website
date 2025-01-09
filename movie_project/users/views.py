import random
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout as auth_logout
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from movies.forms import MovieSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, get_available_genres, filter_queryset, sort, toggle_upcoming
from users.models import CustomList, Favorite, Follow, Profile, Watchlist
from .forms import CustomUserCreationForm, CustomListForm, ProfileImageForm
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q, Avg
from movies.models import Award, Genre, Movie, MovieImage, Review, User
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist


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
            'show_layout_buttons': show_layout_buttons,
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

        form = ProfileImageForm(instance=profile)

        context = {
            'profile': profile,
            'following_count': following_count,
            'followers_count': followers_count,
            'review_count': review_count,
            'form': form
        }

        return render(request, self.template_name, context)

@login_required(login_url='login')
def follow_content(request, model_name, object_id):
    content_type = get_object_or_404(ContentType, model=model_name)

    profile = get_object_or_404(Profile, user=request.user)

    follow = Follow.objects.filter(profile=profile, content_type=content_type, object_id=object_id)
    is_followed = follow.exists()

    if is_followed:
        follow.delete()
        followed = False
    else:
        follow = Follow.objects.create(profile=profile, content_type=content_type, object_id=object_id)
        followed = True

    return JsonResponse({
        'followed': followed
    })


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

    def get(self, request, **kwargs):
        custom_list = self.get_object()
        form = CustomListForm(instance=custom_list)
        custom_list_movies = custom_list.movies.all()

        # Only increment view count if it's the first time this request is being made (not a view_mode toggle)
        if 'view' not in request.GET:
            custom_list.views += 1
            custom_list.save()

        watched_movies_count = custom_list_movies.filter(id__in=request.user.profile.watched_movies.values('id')).count()

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
            'profile': request.user.profile if request.user.is_authenticated else None,
            'custom_list': custom_list,
            'custom_list_movies': custom_list_movies,
            'watched_movies_count': watched_movies_count,
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


# JSONRESPONSE VIEWS

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

    content = get_object_or_404(content_type.model_class(), id=object_id)

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
        'image': content.poster_path.url
    })


@login_required(login_url='/login')
@csrf_exempt
def add_to_list(request, custom_list_id, movie_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        profile = request.user.profile
        movie = Movie.objects.get(id=movie_id)
        custom_list = CustomList.objects.get(profile=profile, id=custom_list_id)

        if movie in custom_list.movies.all():
            custom_list.movies.remove(movie)
            in_custom_list = False
        else:
            custom_list.movies.add(movie)
            in_custom_list = True

        return JsonResponse({
            'movie': {'id': movie.id, 'title': movie.title, 'image': movie.poster_path.url},
            'in_custom_list': in_custom_list,
            'movie_count': custom_list.movies.count()
        })

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Invalid custom list or movie'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# HTMX VIEWS
def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse('<div id="username-error">Username already exists</div>')
    else:
        return HttpResponse('<div id="username-success">Username is available!</div>')

@login_required
def edit_profile_image(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return render(request, 'users/partials/profile-picture.html', {
            'profile': profile
        })
    else:
        form = ProfileImageForm(instance=profile)


@login_required
def edit_custom_list(request, id):
    custom_list = CustomList.objects.get(id=id)
    
    if request.method == 'POST':
        form = CustomListForm(request.POST, instance=custom_list)
        if form.is_valid():
            custom_list = form.save(commit=False)

            movies = form.cleaned_data.get('movies')
            custom_list.movies.set(movies)
            
            custom_list.save()

            header_html = render_to_string('users/partials/list-header-fragment.html', {
                'custom_list': custom_list,
                'custom_list_movies': custom_list.movies.all(),
                'watched_movies_count': custom_list.movies.values('id').filter(id__in=request.user.profile.watched_movies.all()).count(),
                'request': request
            })

            list_content_html = render_to_string('users/partials/list-content-fragment.html', {
                'custom_list': custom_list,
            })

            form_modal_html = render_to_string('users/partials/list-form.html', {
                'custom_list': custom_list,
                "form": CustomListForm(instance=custom_list)
            })

            return HttpResponse(f"""
                                <div class="header" hx-swap-oob="true" id="list-header">{header_html}</div>
                                <div class="content" hx-swap-oob="true" id="list-content">{list_content_html}</div>
                                {form_modal_html}
                                """)
    else:
        return render(request, 'users/partials/list-form.html', {
            'form': CustomListForm(instance=custom_list),
            'custom_list': custom_list
        })
   