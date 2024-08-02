from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from autoslug import AutoSlugField

# Create your models here.
class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
    )

class Movie(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.ImageField(upload_to="media")
    backdrop_path = models.ImageField(upload_to="media")
    release_date = models.DateField()
    genres = models.ManyToManyField('Genre', blank=True, related_name="movies")

    def __str__(self):
        return self.title
    
class Genre(models.Model):
    name = models.CharField(max_length=24)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])

    def __str__(self):
        return f"{self.user}'s Review for {self.movie}: {self.rating} stars"
