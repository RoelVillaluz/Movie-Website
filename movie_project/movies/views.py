from collections import OrderedDict, defaultdict
import json
import os
import random
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import urljoin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, HttpResponseRedirect, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
import requests
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from movies.forms import MovieImageForm, MovieSortForm, PersonImageForm, ReviewForm, ReviewSortForm, SearchForm
from movies.utils import available_actors, available_award_categories, convert_height_to_feet, create_movie_from_api, get_person_accolades, get_available_genres, filter_queryset, get_actors_and_most_popular_movies, get_directors_and_most_popular_movies, get_genre_dict, get_movies_by_month_and_year, get_movies_by_year, get_popular_actors_and_movies, get_similar_movies, get_top_rated_movies, often_works_with, sort, sort_reviews
from users.models import CustomList, Follow, Profile, Watchlist
from .models import Actor, Movie, Genre, Director, MovieImage, Review, PersonImage, Role, User
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Avg, Prefetch, Q
from django.contrib.contenttypes.models import ContentType

def index(request):
    # create_movie_from_api()
    # random_rating(30) # for populating reviews
    # create_users(10)  # for populating users
    today = date.today()
    one_month_before = today - relativedelta(months=1)

    popular_movies = Movie.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:20]
    new_movies = Movie.objects.filter(release_date__gte=one_month_before, release_date__lte=today)
    upcoming_movies = Movie.objects.filter(release_date__gt=today).order_by('release_date')
    popular_genres = Genre.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')[:4]
    popular_actors_and_movie = get_popular_actors_and_movies()
    genre_dict = get_genre_dict(popular_genres)
    top_rated_movies = get_top_rated_movies(5)

    most_popular_reviews = Review.objects.annotate(like_count=Count('likes')).order_by('-like_count').exclude(like_count__lt=1)[:2]

    just_added = Movie.objects.filter(release_date__lte=today).order_by('-id')
    random_movie = Movie.objects.order_by('?').first()

    upcoming_movie_and_date = get_movies_by_month_and_year(upcoming_movies, limit=2)

    popular_lists = CustomList.objects.order_by('-views')[:3]


    context = {
        'popular_movies': popular_movies,
        'new_movies': new_movies,
        'upcoming_movies': upcoming_movies,
        'popular_genres': popular_genres,
        'popular_actors_and_movie': popular_actors_and_movie,
        'genre_dict': genre_dict,
        'top_rated_movies': top_rated_movies,
        'just_added': just_added,
        'random_movie': random_movie,
        'most_popular_reviews': most_popular_reviews,
        'upcoming_movie_and_date': upcoming_movie_and_date,
        'popular_lists': popular_lists,
        'featured_list': popular_lists.first(),
        'profile': request.user.profile if request.user.is_authenticated else None
    }

    return render(request, 'movies/index.html', context)

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie-list.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.all().order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movies = self.get_queryset()

        # Calculate available genres, actors, and award categories with winners before applying filters
        genres_with_movies = get_available_genres(movies)
        award_categories_with_winners = available_award_categories(movies)
        actors_with_movies = available_actors(movies)

        # Filtering logic
        selected_genres = self.request.GET.getlist('genre')
        selected_award_categories = self.request.GET.getlist('award_category')
        selected_actors = self.request.GET.getlist('actor')

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
            movies = Movie.objects.filter(filters)

        # Search form
        search_form = SearchForm(self.request.GET or None)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            movies = movies.filter(title__icontains=query)

        # Sorting logic using the request object
        sort_form = MovieSortForm(self.request.GET or None)
        if sort_form.is_valid():
            sort_by = sort_form.cleaned_data.get('sort_by')
            movies = sort(movies, sort_by)

        movies = movies.distinct()

        # Update context with the necessary data
        context.update({
            'movies': movies,  
            'available_genres': genres_with_movies,
            'award_categories_with_winners': award_categories_with_winners,
            'actors_with_movies': actors_with_movies,
            'selected_genres': selected_genres,
            'selected_award_categories': selected_award_categories,
            'selected_actors': selected_actors,
            'search_form': search_form,
            'sort_form': sort_form,
        })
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie-detail.html'
    context_object_name = 'movie'

    def post(self, request, *args, **kwargs):
        movie = self.get_object()
        form = MovieImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data['image']

            selected_actors = request.POST.getlist('selected_actors')
            selected_directors = request.POST.getlist('selected_directors')

            movie_image = MovieImage.objects.create(movie=movie, image=image)

            if selected_actors:
                actors = Actor.objects.filter(pk__in=selected_actors)
                movie_image.actors.set(actors)

            if selected_directors:
                directors = Director.objects.filter(pk__in=selected_directors)
                movie_image.directors.set(directors)

            return redirect(request.META.get('HTTP_REFERER', 'index'))
        
        return redirect('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        director = movie.directors.first()

        # Get the roles associated with the movie
        roles = Role.objects.filter(
            content_type=ContentType.objects.get_for_model(movie),
            object_id=movie.id
        )
        
        actor_roles = {actor.id: None for actor in movie.actors.all()}
        for role in roles:
            if role.actor.id in actor_roles:
                actor_roles[role.actor.id] = role.character

        all_images_count = len(movie.images.all())

        context.update({
            'director': director,
            'director_movies': director.movies.exclude(id=movie.id) if director else None,
            'overview_images': movie.images.all()[:2] if movie.images.count() >= 2 else None,
            'top_reviews': movie.reviews.order_by('-rating')[:2],
            'awards_by_name': self.get_awards_by_name(movie),
            'people_in_film': list(movie.actors.all()) + list(movie.directors.all()),
            'actor_roles': actor_roles,
            'all_images_count': all_images_count,
            'more_images_count': max(all_images_count - 4, 0),
            'similar_movies': get_similar_movies(movie),
            'form': MovieImageForm()
        })

        return context

    def get_awards_by_name(self, movie):
        awards_by_name = defaultdict(lambda: {'awards': [], 'win_count': 0, 'nomination_count': 0})
        for award in movie.awards.all():
            awards_by_name[award.award_name]['awards'].append(award)
            awards_by_name[award.award_name]['nomination_count'] += 1
            if award.winner:
                awards_by_name[award.award_name]['win_count'] += 1
        return dict(awards_by_name)

class GenreListView(ListView):
    model = Genre
    context_object_name = 'genres'
    template_name = 'movies/genre-list.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        genres_with_backdrops = []
        genre_set = set()
        genres = Genre.objects.all()
        today = date.today()

        # Assign random movie backdrop_path to each genre
        for genre in genres:
            movies_in_genre = genre.movies.exclude(pk__in=genre_set)
            if movies_in_genre.exists():
                random_movie = random.choice(movies_in_genre)
                genre_set.add(random_movie.pk)
                genres_with_backdrops.append({
                    'id': genre.pk,
                    'name': genre.name,
                    'backdrop_path': random_movie.backdrop_path.url,
                })

        # Filter out genres without movies and order by name
        genres_with_backdrops = sorted(genres_with_backdrops, key=lambda x: x['name'])

        context.update({
            'genres': genres_with_backdrops,
        })

        return context


class GenreDetailView(DetailView):
    model = Genre
    template_name = 'movies/genre-movies.html'
    context_object_name = 'genre'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movies = self.object.movies.all()

        context.update({
            'movies': movies,
            'main_image': movies.first().backdrop_path.url if movies.exists() else None,
        })

        return context
    
class PersonDetailView(DetailView):
    template_name = 'movies/person-detail.html'

    def dispatch(self, request, *args, **kwargs):
        model_name = kwargs.get('model_name')

        if model_name == 'actors':
            self.model = Actor
            self.person_type = 'actor'
        elif model_name == 'directors':
            self.model = Director
            self.person_type = 'director'
        else:
            raise Http404("Person type not found.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])
    
    def post(self, request, *args, **kwargs):
        person = self.get_object()
        form = PersonImageForm(request.POST, request.FILES)

        if form.is_valid():
            content_type = ContentType.objects.get_for_model(person)

            PersonImage.objects.create(
                image=form.cleaned_data['image'],
                content_type=content_type,
                object_id=person.id
            )
            return redirect(request.META.get('HTTP_REFERER', 'person-detail'))
        
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.get_object()
        
        # Ensure person_type is set
        if not hasattr(self, 'person_type'):
            model_name = self.kwargs.get('model_name')
            if model_name == 'actors':
                self.person_type = 'actor'
            elif model_name == 'director':
                self.person_type = 'director'
        
        # Set specific context for Actor or Director
        most_popular_movie = person.most_popular_movie if self.person_type == 'actor' else person.most_popular_movie()
        co_workers = often_works_with(person)
        accolades = get_person_accolades(person)
        
        # Images
        person_images = PersonImage.objects.filter(content_type=ContentType.objects.get_for_model(self.model), object_id=person.id)
        person_movie_images = MovieImage.objects.filter(actors=person) if self.person_type == 'actor' else MovieImage.objects.filter(directors=person)
        
        all_person_images = list(person_images) + list(person_movie_images)
        all_images_count = len(all_person_images)
        
        # Follower status
        profile = Profile.objects.get(user=self.request.user) if self.request.user.is_authenticated else None
        is_following = Follow.objects.filter(
            profile=profile,
            content_type=ContentType.objects.get_for_model(person),
            object_id=person.id
        ).exists() if profile else False
        
        # Known for section
        if self.person_type == 'actor':
            known_for = person.movies.annotate(review_count=Count('reviews')).order_by('-review_count')[:4]
            avg_movie_rating = person.movies.aggregate(Avg('reviews__rating'))
        else:
            known_for = person.movies.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4]
            avg_movie_rating = None  # Directors may not need this
        
        context.update({
            'person': person,
            'movies': person.movies.all(),
            'rank': person.get_rank(),
            'follower_count': person.follower_count,
            'most_popular_movie': most_popular_movie,
            'is_following': is_following,
            'age': person.get_age,
            'default_bio': person.default_bio,
            'co_workers': co_workers,
            'accolades': accolades,
            'all_person_images': all_person_images[:4],
            'all_images_count': all_images_count + 1,
            'more_images_count': max(all_images_count - 4, 0),
            'person_type': self.person_type,
            'known_for': known_for,
            'avg_movie_rating': avg_movie_rating,
            'form': PersonImageForm(),
        })

        return context
    
class MovieImagesView(DetailView):
    model = Movie
    template_name = 'movies/movie-images.html'
    context_object_name = 'movie'

    def post(self, request, *args, **kwargs):
        movie = self.get_object()
        form = MovieImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data['image']

            selected_actors = request.POST.getlist('selected_actors')
            selected_directors = request.POST.getlist('selected_directors')

            movie_image = MovieImage.objects.create(movie=movie, image=image)

            if selected_actors:
                actors = Actor.objects.filter(pk__in=selected_actors)
                movie_image.actors.set(actors)

            if selected_directors:
                directors = Director.objects.filter(pk__in=selected_directors)
                movie_image.directors.set(directors)

            return redirect(request.META.get('HTTP_REFERER', 'index'))
        
        return redirect('index')
    
    def get(self, request, *args, **kwargs):
        movie = self.get_object()
        all_images = movie.images.all()

        roles = Role.objects.filter(actor_id__in=movie.actors.all())

        actor_roles = {actor.id: None for actor in movie.actors.all()}
        for role in roles:
            if role.actor.id in actor_roles:
                actor_roles[role.actor.id] = role.character

        context = {
            'movie': movie,
            'all_images': all_images,
            'actor_roles': actor_roles,
            'people_in_film': list(movie.actors.all()) + list(movie.directors.all()),
            'form': MovieImageForm()
        }

        return render(request, self.template_name, context)
    
class PersonImagesView(DetailView):
    template_name = 'movies/person-images.html'
    context_object_name = 'person'

    def get_queryset(self):
        model_name = self.kwargs['model_name']
        if model_name == 'actors':
            return Actor.objects.all()
        elif model_name == 'directors':
            return Director.objects.all()
        else:
            raise ValueError("Error: Invalid Model")
        
    def post(self, request, *args, **kwargs):
        person = self.get_object()
        form = PersonImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            content_type = ContentType.objects.get_for_model(person)

            PersonImage.objects.create(
                image=form.cleaned_data['image'],
                content_type=content_type,
                object_id=person.id
            )

            return redirect(request.META.get('HTTP_REFERER', 'person_images'))
        
        # If form is not valid, re-render the page with form errors
        return self.get(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        person = self.get_object()

        if isinstance(person, Actor):
            movie_images = MovieImage.objects.filter(actors=person)
            person_type = 'actors'
        else:
            movie_images = MovieImage.objects.filter(directors=person)
            person_type = 'directors'

        person_images = PersonImage.objects.filter(content_type=ContentType.objects.get_for_model(person), object_id=person.id)
        all_images = list(movie_images) + list(person_images)

        # use later for filtering co actors included in the image and/or movie of the image
        selected_co_actors = request.GET.getlist('co_actors')
        selected_movies = request.GET.getlist('movies')

        filters = Q()

        # filter images with other actors present in the image
        if selected_co_actors:
            co_actors_q = Q()
            for co_actor in co_actors_q:
                co_actors_q |= Q(actor__name=co_actor)
            filters |= co_actors_q

        context = {
            'person': person,
            'all_images': all_images,
            'person_type': person_type,
            'form': PersonImageForm()
        }

        return render(request, self.template_name, context)
    
@login_required(login_url='/login')
@csrf_exempt
def add_to_watchlist(request, id):
    user = request.user
    movie = Movie.objects.get(id=id)
    
    # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Access the watchlist from the profile
    watchlist = profile.watchlist

    watched = None

    if movie not in watchlist.movies.all():
        watchlist.movies.add(movie)
        if movie in profile.watched_movies.all():
            profile.watched_movies.remove(movie)
            watched = False

        watchlisted = True
    else:
        watchlist.movies.remove(movie)
        watchlisted = False

    watchlist.save()

    return JsonResponse({
        'watchlisted': watchlisted,
        'watched': watched, 
        'movie_image': movie.poster_path.url
    })


def like_review(request, id):
    user = request.user
    review = get_object_or_404(Review, id=id)

    if user in review.likes.all():
        review.likes.remove(user)
        liked = False
    else:
        review.likes.add(user)
        liked = True
    
    like_count = review.likes.count()

    return JsonResponse({
        'liked': liked,
        'like_count': like_count
    })

class SearchView(View):
    form_class = SearchForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET)
        query = ''
        movies = actors = directors = None
        selected_filter = request.GET.get('filter', 'all')  # Default to 'all' if no filter is provided
        
        if form.is_valid():
            query = form.cleaned_data.get('query', '')

            # Create a dictionary to map filters to their corresponding querysets
            filters = {
                'movies': Movie.objects.filter(title__icontains=query).order_by('title'),
                'actors': Actor.objects.filter(name__icontains=query).order_by('name'),
                'directors': Director.objects.filter(name__icontains=query).order_by('name')
            }

            # Apply the filter based on the selected filter type
            if selected_filter in filters:
                if selected_filter == 'movies':
                    movies = filters['movies']
                elif selected_filter == 'actors':
                    actors = filters['actors']
                elif selected_filter == 'directors':
                    directors = filters['directors']
            else:
                # If 'all' or an unknown filter is selected, retrieve all types
                movies = filters['movies']
                actors = filters['actors']
                directors = filters['directors']

        return render(request, 'movies/search_results.html', {
            'form': form,
            'movies': movies,
            'actors': actors,
            'directors': directors,
            'query': query,
            'selected_filter': selected_filter,
        })
    

class SearchSuggestionsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')

        movie_results = []
        actor_results = []
        director_results = []

        if query:
            # Get all matching movies without limiting the results
            all_matching_movies = Movie.objects.filter(title__icontains=query).prefetch_related(
                Prefetch('genres', queryset=Genre.objects.all())
            )

            # Get the first 3 matching movies
            movie_suggestions = all_matching_movies[:2]

            all_matching_actors = Actor.objects.filter(name__icontains=query)
            actor_suggestions = all_matching_actors[:2]

            all_matching_directors = Director.objects.filter(name__icontains=query)
            director_suggestions = all_matching_directors[:1]  

            for movie in movie_suggestions:
                # Get all genres for the movie
                all_genres = [genre.name for genre in movie.genres.all()]
                avg_rating = movie.avg_rating()
                # Choose only the first genre
                genre = all_genres[0] if all_genres else 'None'

                movie_results.append({
                    'id': movie.id,
                    'title': movie.title,
                    'avg_rating': avg_rating,
                    'year': movie.release_date.year,
                    'poster_path': movie.poster_path.url,
                    'genre': genre  
                })

            # Get actor suggestions and their most popular movie
            actor_and_most_popular_movie = get_actors_and_most_popular_movies(actor_suggestions, 1)

            actor_results = [{
                'id': actor.id,
                'name': actor.name,
                'image': actor.image.url,
                'most_popular_movie': actor_movie,
            } for actor, actor_movie in actor_and_most_popular_movie.items()]

            director_and_most_popular_movie = get_directors_and_most_popular_movies(director_suggestions, 1)

            # Get director suggestions
            director_results = [{
                'id': director.id,
                'name': director.name,
                'image': director.image.url,
                'most_popular_movie': director_movie,
            } for director, director_movie in director_and_most_popular_movie.items()]

        # Calculate the total number of matching searches
        total_matching_movies = all_matching_movies.count()
        total_matching_actors = all_matching_actors.count()
        total_matching_directors = all_matching_directors.count()

        return JsonResponse({
            'movies': movie_results,
            'movie_count': total_matching_movies,  
            'actors': actor_results,
            'actor_count': total_matching_actors,
            'directors': director_results,
            'director_count': total_matching_directors
        })
    
class GetMovieImageDataView(View):
    def get(self, request, *args, **kwargs):
        movie_images = MovieImage.objects.all()
        person_images = PersonImage.objects.all()
        image_data = []

        for image in movie_images:
            data = {
                'image_url': image.image.url,
                'movie': str(image.movie) if image.movie else None,
                'year': image.movie.release_date.year if image.movie else None,
                'movie_id': image.movie.id if image.movie else None,
                'type': 'movie',
                'people': image.people_in_image(),
                'id': image.pk
            }
            image_data.append(data)

        for image in person_images:
            content_type = image.content_type.model
            data = {
                'image_url': image.image.url,
                'name': image.content_object.name if content_type in ['actor', 'director'] else None,
                'person_id': image.content_object.id if content_type in ['actor', 'director'] else None,
                'type': content_type,
                'people': [],
                'id': image.pk
            }
            image_data.append(data)

        return JsonResponse(image_data, safe=False)

class EditPersonImageView(DetailView):
    template_name = 'movies/edit-person-image.html'

    def dispatch(self, request, *args, **kwargs):
        model_name = kwargs.get('model_name')

        if model_name == 'actors':
            self.model = Actor
            self.person_type = 'actors'
        elif model_name == 'directors':
            self.model = Director
            self.person_type = 'directors'
        else:
            raise Http404("Person type not found.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        person_image = get_object_or_404(PersonImage, pk=self.kwargs['pk'])

        if not isinstance(person_image.content_object, self.model):
            raise Http404("Person image not associated with the correct model.")

        return person_image

    def post(self, request, *args, **kwargs):
        image = self.get_object()
        form = PersonImageForm(request.POST, request.FILES, instance=image)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('person-detail', args=[self.person_type, image.content_object.pk]))
        else:
            return self.render_to_response({'form': form, 'person_type': self.person_type, 'person_image': image})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object()

        # Ensure person_type is set
        if not hasattr(self, 'person_type'):
            model_name = self.kwargs.get('model_name')
            if model_name == 'actors':
                self.person_type = 'actor'
            elif model_name == 'director':
                self.person_type = 'director'

        context.update({
            'form': PersonImageForm(instance=image),
            'image': image,
            'person': image.content_object,
            'person_type': self.person_type
        })

        return context

class EditMovieImageView(DetailView):
    model = MovieImage
    template_name = 'movies/edit-image-form.html'
    context_object_name = 'image'

    @method_decorator(login_required)  # Ensure the user is logged in
    def post(self, request, *args, **kwargs):
        image = self.get_object()
        form = MovieImageForm(request.POST, request.FILES, instance=image)

        if form.is_valid():
            form.save()

            selected_actors = request.POST.getlist('selected_actors')
            selected_directors = request.POST.getlist('selected_directors')

            if selected_actors:
                actors = Actor.objects.filter(pk__in=selected_actors)
                image.actors.set(actors)

            if selected_directors:
                directors = Director.objects.filter(pk__in=selected_directors)
                image.directors.set(directors)

            return HttpResponseRedirect(reverse("movie-detail", args=[image.movie.id]))
        
        return redirect('index')

    @method_decorator(login_required)  # Ensure the user is logged in
    @method_decorator(permission_required('movies.change_movieimage', raise_exception=True))  # Check permission
    def get(self, request, *args, **kwargs):
        image = self.get_object()
        movie = image.movie
        form = MovieImageForm(instance=image)

        roles = Role.objects.filter(
            content_type=ContentType.objects.get_for_model(movie),
            object_id=movie.id
        )

        actor_roles = {actor.id: None for actor in movie.actors.all()}
        for role in roles:
            if role.actor.id in actor_roles:
                actor_roles[role.actor.id] = role.character

        context = {
            'image': image,
            'people_in_film': list(movie.actors.all()) + list(movie.directors.all()),
            'actor_roles': actor_roles,
            'form': form
        }
        return render(request, self.template_name, context)

    def get_object(self):
        # Use 'id' instead of 'pk' if you want to keep 'id' in the URL
        return get_object_or_404(self.model, id=self.kwargs['id'])
    
class DeleteMovieImageView(DeleteView):
    model = MovieImage
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('movie-detail')

    def delete(self):
        self.object = self.get_object()
        self.object.delete()

    def get_success_url(self):
        movie_id = self.object.movie.id  
        return reverse_lazy('movie-detail', kwargs={'pk': movie_id})
    
class DeletePersonImageView(DeleteView):
    model = PersonImage

    def dispatch(self, request, *args, **kwargs):
        model_name = kwargs.get('model_name')

        if model_name == 'actors':
            self.model = Actor
            self.person_type = 'actors'
        elif model_name == 'directors':
            self.model = Director
            self.person_type = 'directors'
        else:
            raise Http404("Person type not found.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        person_image = get_object_or_404(PersonImage, pk=self.kwargs['pk'])

        if not isinstance(person_image.content_object, self.model):
            raise Http404("Person image not associated with the correct model.")

        return person_image

    def get_success_url(self):
        image = self.get_object()
        person_pk = image.content_object.pk
        return reverse('person-detail', kwargs={'model_name': self.person_type, 'pk': person_pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.get_object()
        
        # Ensure person_type is set
        if not hasattr(self, 'person_type'):
            model_name = self.kwargs.get('model_name')
            if model_name == 'actors':
                self.person_type = 'actor'
            elif model_name == 'director':
                self.person_type = 'director'

        context.update({
            'person': person,
            'person_type': self.person_type
        })

        return context

    def delete(self):
        self.object = self.get_object()
        self.object.delete()

@login_required
def add_review(request, id):
    movie = Movie.objects.get(id=id)
    # if not movie.reviews.filter(user=request.user).exists():
    if request.method == 'POST':
        reviewed = movie.reviews.filter(user__id=request.user.id).exists()
        try:
            # Parse JSON body
            data = json.loads(request.body)
            description = data.get('description')
            rating = data.get('rating')

            if reviewed:
                return JsonResponse({
                    'success': False,
                    'message': 'You have already reviewed this movie',
                    'reviewed': reviewed,
                })

            if rating:
                review = Review.objects.create(user=request.user, movie=movie, description=description, rating=rating)
                return JsonResponse({
                        'success': True, 
                        'message': f'Review for {movie.title} created successfuly',
                        'movie': {'title': movie.title, 'image': movie.poster_path.url},
                        'rating': review.rating
                    })
            else:
                return JsonResponse({'success': False, 'message': 'Error: missing rating'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format'}, status=400)
        
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

class MovieReviewListView(ListView):
    model = Movie
    template_name = 'movies/review-list.html'
    context_object_name = 'reviews'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = get_object_or_404(Movie, pk=self.kwargs.get('pk'))

        sort_by = self.request.GET.get('sort_by', None)
        hide_spoilers = self.request.GET.get('hide_spoilers')
        following = self.request.GET.get('following')
        my_reviews = self.request.GET.get('my_reviews')
        
        reviews = movie.reviews.all()

        if sort_by:
            reviews = sort_reviews(reviews, sort_by)

        sort_form = ReviewSortForm(initial={'sort_by': sort_by})
        
        if hide_spoilers:
            reviews = reviews.exclude(has_spoilers=True)

        for review in reviews:
            reviewer = review.user

        # show reviews where user is followed
        if following:
            # get content type for profile first 
            profile_content_type = ContentType.objects.get_for_model(Profile)

            # filter follow objects that have content type of profile
            followed_profiles = self.request.user.profile.follows.filter(content_type=profile_content_type)

            # get profile IDs
            profile_ids = [profile.content_object.id for profile in followed_profiles]

            reviews = reviews.filter(user__id__in=profile_ids)

        if my_reviews:
            reviews = reviews.filter(user__id=self.request.user.id)


        context.update({
            'movie': movie,
            'reviews': reviews,
            'review_count': reviews.count,
            'sort_form': sort_form,
            'hide_spoilers': hide_spoilers,
            'following': following,
            'my_reviews': my_reviews
        })

        return context


class CustomListListView(ListView):
    model = CustomList
    template_name = 'movies/custom-lists.html'
    context_object_name = 'custom_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            "custom_lists": CustomList.objects.all()
        })
        

        return context