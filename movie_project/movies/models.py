import random
from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from autoslug import AutoSlugField
from django.db.models import Avg, F, Window
from django.db.models.functions import Rank
from moviepy.editor import VideoFileClip
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

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

    def __str__(self):
        return f"{self.movie} Image"
    
class MovieVideo(models.Model):
    movie = models.ForeignKey(Movie, related_name="videos", blank=True, null=True, on_delete=models.CASCADE)
    name = models.TextField()
    video = models.FileField(upload_to="videos", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="thumbnails", blank=True, null=True)

    def __str__(self):
        return self.name

    def generate_thumbnail_from_video(self):
        if not self.video:
            return

        video_path = self.video.path
        video = VideoFileClip(video_path)
        
        # Random timestamp
        duration = video.duration
        random_time = random.uniform(0, duration)
        
        # Extract a frame
        frame = video.get_frame(random_time)
        image = Image.fromarray(frame)
        
        # Save the image to a BytesIO object
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG')
        thumb_io.seek(0)

        # Save the thumbnail to the model's thumbnail field
        thumbnail_name = f"{self.name}_thumbnail.jpg"
        self.thumbnail.save(thumbnail_name, ContentFile(thumb_io.read()), save=False)

        # Close the BytesIO stream
        thumb_io.close()

    def save(self, *args, **kwargs):
        # Generate a thumbnail from the video if it does not already exist
        if self.video and not self.thumbnail:
            self.generate_thumbnail_from_video()
        super(MovieVideo, self).save(*args, **kwargs)

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
    bio = models.TextField(default="No bio yet.")

    def __str__(self):
        return self.name

    def avg_movie_rating(self):
        avg_rating = self.movies.aggregate(average=Avg('reviews__rating'))['average']
        return avg_rating or 0

    @staticmethod
    def ranked_actors():
        return Actor.objects.annotate(avg_rating=Avg('movies__reviews__rating')).order_by('-avg_rating')

    def get_rank(self): # update later and add followers so rankings can be more objective and reduce number of ties
        ranked_actors = Actor.ranked_actors().annotate(rank=Window(expression=Rank(), order_by=F('avg_rating').desc()))
        for actor in ranked_actors:
            if actor.pk == self.pk:
                return actor.rank
        return None

class Director(models.Model):
    name = models.CharField(max_length=50)
    bio = models.TextField(default="No bio yet.")
    # awards = models.ForeignKey(Award)
    image = models.ImageField(upload_to="media", default="media/default.jfif")
    movies = models.ManyToManyField(Movie, related_name="directors")

    def __str__(self):
        return self.name