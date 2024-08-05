from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Actor, Director, Movie, Genre, MovieImage, Review, User

# Register your models here.
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(User)
admin.site.register(MovieImage)

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

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_genres')
    search_fields = ('title', 'display_genres')
    list_filter = ('genres', ReleaseYearListFilter)

    def display_genres(self, obj):
        genres = obj.genres.all()[:3]
        return ', '.join([genre.name for genre in genres]) + ('...' if len(genres) > 3 else ' ')
    display_genres.short_description = 'Genres'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'genres':
            kwargs['queryset'] = Genre.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    # do the same later for movies, alphabetize movies for review model admin

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating')
    search_fields = ('movie__title', 'rating')