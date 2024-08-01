from django.contrib import admin

from .models import Movie, Genre, Review

# Register your models here.
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Review)