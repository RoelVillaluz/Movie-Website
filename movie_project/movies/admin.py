from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Movie, Genre, Review

# Register your models here.
admin.site.register(Genre)
admin.site.register(Review)

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