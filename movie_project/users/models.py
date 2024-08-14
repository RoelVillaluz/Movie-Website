from django.conf import settings
from django.db import models
from movies.models import User, Movie

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    watchlist = models.ForeignKey('Watchlist' ,related_name="profiles", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
class Watchlist(models.Model):
    movies = models.ManyToManyField(Movie, related_name="watchlists")

    def __str__(self):
        return  f"{self.user}'s watchlist"