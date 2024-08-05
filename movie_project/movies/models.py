from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from autoslug import AutoSlugField
from django.db.models import Avg

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
    actors = models.ManyToManyField('Actor', blank=True, related_name="movies")
    hours = models.PositiveIntegerField(default=0)
    minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def runtime(self):
        return f"{self.hours} hours {self.minutes} minutes"
    
    def avg_rating(self):
        avg_rating = self.reviews.aggregate(average=Avg('rating'))['average']
        return avg_rating or 0
    
class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="movie_images")
    
class Genre(models.Model):
    name = models.CharField(max_length=24)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    
    description = models.TextField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])

    def __str__(self):
        return f"{self.user}'s Review for {self.movie}: {self.rating} stars"

class Actor(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media", default="media/default.jfif")

    def __str__(self):
        return self.name
    
class Director(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media", default="media/default.jfif")
    movies = models.ManyToManyField(Movie, related_name="directors")

    def __str__(self):
        return self.name