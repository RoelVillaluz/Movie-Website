from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Actor, Award, Director, Movie, Genre, MovieImage, MovieVideo, Review, User

# Register your models here.
admin.site.register(Genre)
admin.site.register(Director)
admin.site.register(User)
admin.site.register(MovieImage)
admin.site.register(MovieVideo)
admin.site.register(Award)

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
    
class MovieInline(admin.TabularInline):
    model = Actor.movies.through
    extra = 1

class ActorInline(admin.TabularInline):
    model = Movie.actors.through
    extra = 1

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_genres', 'display_actors')
    search_fields = ('title', 'genres__name', 'actors__name')
    list_filter = ('genres', ReleaseYearListFilter)
    inlines = [ActorInline]


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
    

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_movies')
    search_fields = ('name', 'movies__title')
    inlines = [MovieInline]

    def display_movies(self, obj):
        movies = obj.movies.all()[:3]
        return ', '.join([movie.title for movie in movies]) + ('...' if len(movies) > 3 else ' ')
    display_movies.short_description = 'Movies'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating')
    search_fields = ('movie__title', 'rating')