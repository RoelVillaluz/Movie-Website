from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from movies.admin import HasMoviesFilter
from .models import Follow, Profile, Watchlist

# Register your models here.
admin.site.register(Watchlist)

class FollowAdminForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict content types to User, Actor, and Director
        content_types = ContentType.objects.filter(model__in=['user', 'actor', 'director'])
        self.fields['content_type'].queryset = content_types

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    form = FollowAdminForm

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )
    search_fields = ('user__username', )
    autocomplete_fields = ('watched_movies', )