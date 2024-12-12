from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from movies.admin import HasMoviesFilter
from .models import CustomList, Favorite, Follow, Profile, Watchlist

admin.site.register(CustomList)
admin.site.register(Favorite)

# Register your models here.
class FollowAdminForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict content types to User, Actor, and Director
        content_types = ContentType.objects.filter(model__in=['profile', 'actor', 'director'])
        self.fields['content_type'].queryset = content_types

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    form = FollowAdminForm

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__username', )
    autocomplete_fields = ('watched_movies', )

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_movies')
    search_fields = ('user__username', 'movies__title')

    def display_movies(self, obj):
        movies = obj.movies.all()[:3]
        return ', '.join([movie.title for movie in movies]) + ('...' if len(movies) > 3 else '')
    display_movies.short_description = 'Movies in watchlist'