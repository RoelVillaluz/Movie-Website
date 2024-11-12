from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    watchlist = models.ForeignKey('Watchlist' ,related_name="profiles", on_delete=models.CASCADE)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    watched_movies = models.ManyToManyField('movies.Movie', blank=True, related_name='watched_by')

    def __str__(self):
        return self.user.username
    
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    movies = models.ManyToManyField('movies.Movie', related_name="watchlists", null=True, blank=True)

    def __str__(self):
        return  f"{self.user}'s watchlist"
    
class Follow(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="follows")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.profile.user.username} follows {self.content_object}'
    
class CustomList(models.Model):
    PRIVACY_CHOICES = [
        ('friends', 'Friends'),
        ('everyone', 'Everyone'),
        ('only_me', 'Only Me')
    ]

    name = models.TextField()
    description = models.TextField(blank=True)
    profile = models.ForeignKey(Profile, related_name="lists", on_delete=models.CASCADE)
    movies = models.ManyToManyField('movies.Movie', related_name='lists', blank=True)
    privacy = models.TextField(choices=PRIVACY_CHOICES, default='everyone')
    ranked_list = models.BooleanField(default=False)

    def __str__(self):
        return f"'{self.name}' by {self.profile.user}"