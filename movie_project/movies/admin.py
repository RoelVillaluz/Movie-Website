from typing import Any
from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from .models import Actor, Award, Character, Director, Movie, Genre, MovieImage, MovieVideo, PersonImage, Review, Role, User
from django.contrib.contenttypes.models import ContentType


# Register your models here.
admin.site.register(User)
admin.site.register(MovieImage)
admin.site.register(MovieVideo)
admin.site.register(Character)
admin.site.register(Role)

class ReleaseYearListFilter(admin.SimpleListFilter):
    title = _('release year')
    parameter_name = 'release_year'

    def lookups(self, request, model_admin):
        years = set()
        for movie in model_admin.model.objects.all():
            years.add(movie.release_date.year)
        return sorted([(year, year) for year in years], reverse=True)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(release_date__year=self.value())
        return queryset
    
class HasMoviesFilter(admin.SimpleListFilter):
    title = 'Has movies'
    parameter_name = 'movies'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(movies__isnull=False).distinct()
        elif self.value() == 'no':
            return queryset.filter(movies__isnull=True).distinct()
  
        return queryset
    
class HasImagesFilter(admin.SimpleListFilter):
    title = 'Has Images'
    parameter_name = 'images'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(movie_images__isnull=False).distinct()
        else:
            return queryset.filter(movie_images__isnull=True).distinct()
        
        return queryset
    
class ThroughModelInline(admin.TabularInline):
    model = None
    extra = 1

    def __init__(self, parent_model, admin_site, model=None):
        if model:
            self.model = model
        super().__init__(parent_model, admin_site)

class ActorInline(ThroughModelInline):
    model = Movie.actors.through

class DirectorInline(ThroughModelInline):
    model = Movie.directors.through

class GenreInline(ThroughModelInline):
    model = Movie.genres.through

class AwardInline(admin.TabularInline):
    model = Award
    extra = 1

    def __init__(self, parent_model, admin_site):
        super().__init__(parent_model, admin_site)

def create_inline(through_model):
    """
    Helper function to create dynamic inlines for models with ManyToMany 'through' relationships.
    """
    return type('DynamicInline', (ThroughModelInline,), {'model': through_model})

class PersonImageForm(forms.ModelForm):
    class Meta:
        model = PersonImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_types = ContentType.objects.filter(model__in=['actor', 'director', 'profile'])
        self.fields['content_type'].queryset = content_types

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_genres', 'display_actors')
    search_fields = ('title', 'genres__name', 'actors__name')
    list_filter = ('genres', ReleaseYearListFilter)
    autocomplete_fields = ('actors', 'directors')
    inlines = [create_inline(Movie.actors.through), 
               create_inline(Movie.directors.through), 
               create_inline(Movie.genres.through),
               AwardInline
               ]

    def display_genres(self, obj):
        genres = obj.genres.all()[:3]
        return ', '.join([genre.name for genre in genres]) + ('...' if len(genres) > 3 else ' ')
    display_genres.short_description = 'Genres'

    def display_actors(self, obj):
        actors = obj.actors.all()[:3]
        return ', '.join([actor.name for actor in actors]) + ('...' if len(actors) > 3 else ' ')
    display_actors.short_description = 'Actors'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'genres':
            kwargs['queryset'] = Genre.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    # do the same later for movies, alphabetize movies for review model admin

@admin.register(PersonImage)
class PersonImageAdmin(admin.ModelAdmin):
    form = PersonImageForm

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_movies')
    search_fields = ('name', 'movies__title')
    list_filter = (HasMoviesFilter, HasImagesFilter)
    inlines = [create_inline(Movie.actors.through)]
    ordering = ('name',)

    def display_movies(self, obj):
        movies = obj.movies.all()[:3]
        return ', '.join([movie.title for movie in movies]) + ('...' if len(movies) > 3 else ' ')
    display_movies.short_description = 'Movies'

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_movies')
    search_fields = ('name', 'movies__title')
    list_filter = (HasMoviesFilter, HasImagesFilter)
    inlines = [create_inline(Movie.directors.through)]
    ordering = ('name',)

    def display_movies(self, obj):
        movies = obj.movies.all()[:3]
        return ', '.join([movie.title for movie in movies]) + ('...' if len(movies) > 3 else ' ')
    display_movies.short_description = 'Movies'

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_movies')
    search_fields = ('name', 'movies__title')
    inlines = [create_inline(Movie.genres.through)]
    ordering = ('name',)

    def display_movies(self, obj):
        movies = obj.movies.all()[:3]
        return ', '.join([movie.title for movie in movies]) + ('...' if len(movies) > 3 else ' ')
    display_movies.short_description = 'Movies'

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'category', 'year', 'winner')
    list_filter = ('category', 'winner')
    search_fields = ('category', 'movie__title', 'actor__name', 'director__name', 'year')
    ordering = ('-year',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating')
    search_fields = ('movie__title', 'rating', 'user__username')