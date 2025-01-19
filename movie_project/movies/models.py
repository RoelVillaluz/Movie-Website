from datetime import date, timezone
import random
from django import db
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import Avg, F, Window, Count
from django.db.models.functions import Rank
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from moviepy import VideoFileClip
from django.utils.timezone import now

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
    overview = models.TextField(default="No overview yet")
    poster_path = models.ImageField(upload_to="media")
    backdrop_path = models.ImageField(upload_to="media")
    release_date = models.DateField(default=now)
    genres = models.ManyToManyField('Genre', blank=True, related_name="movies")
    actors = models.ManyToManyField('Actor', blank=True, related_name="movies")
    hours = models.PositiveIntegerField(default=0)
    minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def runtime(self):
        return f"{self.hours}h {self.minutes}m"
    
    def avg_rating(self):
        avg_rating = self.reviews.aggregate(average=Avg('rating'))['average']
        return avg_rating or 0
    
    # use later to make dynamic function to display if content is movie or series
    def get_class_name(self):
        return self.__class__.__name__

    
class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="movie_images")
    actors = models.ManyToManyField('Actor', related_name='movie_images', blank=True)
    directors = models.ManyToManyField('Director', related_name='movie_images', blank=True)

    def __str__(self):
        people = self.people_in_image()
        people_names = ', '.join([person['name'] for person in people])
        return f"{self.movie} Image: {people_names}"
    
    def people_in_image(self):
        actors_data = [{'id': actor.id, 'name': actor.name, 'type': 'actor'} for actor in self.actors.all()]
        directors_data = [{'id': director.id, 'name': director.name, 'type': 'director'} for director in self.directors.all()]

        all_people_in_image = list(actors_data) + list(directors_data)

        return all_people_in_image
    
class MovieVideo(models.Model):
    movie = models.ForeignKey(Movie, related_name="videos", blank=True, null=True, on_delete=models.CASCADE)
    name = models.TextField()
    video = models.FileField(upload_to="videos", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="thumbnails", blank=True, null=True)

    def __str__(self):
        return self.name
    
    # @property
    # def duration(self):
    #     if self.video:
    #         video = VideoFileClip(self.video.path)
    #         return video.duration
    #     return 0
    
    @property
    def duration_formatted(self):
        total_seconds = self.duration
        minutes, seconds = divmod(int(total_seconds), 60)
        return f"{minutes}m {seconds}s"

class Genre(models.Model):
    name = models.CharField(max_length=24)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    description = models.TextField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    likes = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    created_on = models.DateTimeField(default=now)
    has_spoilers = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_review')
        ]

    def __str__(self):
        return f"{self.user}'s Review for {self.movie}: {self.rating} stars"

    def total_likes(self):
        return self.likes.count()
    
    def formatted_date(self):
        return self.created_on.strftime('%B %d, %Y') # string format example: January 16, 2025 
    
class PersonImage(models.Model):
    image = models.ImageField(upload_to="person_images")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.content_object}'s image"
    
class Character(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Role(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    character = models.ForeignKey(Character, related_name='roles', on_delete=models.SET_NULL, null=True)  # Use SET_NULL to avoid errors
    actor = models.ForeignKey('Actor', related_name='roles', on_delete=models.CASCADE)

    def __str__(self):
        character_name = self.character.name if self.character else "Unknown Character"
        return f"{character_name} in {self.content_object}"

class Actor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Non-Binary'),
    ]

    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media", default="media/default.jfif")
    bio = models.TextField(default="No bio yet.")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="Not specified")
    birth_place = models.CharField(max_length=100, default="Not specified")
    nationality = models.CharField(max_length=50, default="Not specified")
    birth_date = models.DateField(default='2000-01-01')
    height = models.IntegerField(default=0)
    images = models.ManyToManyField('PersonImage', related_name='actors', blank=True)
    roles = GenericRelation(Role)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name
    
    def get_age(self):
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def avg_movie_rating(self):
        avg_rating = self.movies.aggregate(average=Avg('reviews__rating'))['average']
        return avg_rating or 0
    
    def most_popular_movie(self):
        most_popular_movie = self.movies.annotate(review_count=Count('reviews')).order_by('-review_count').first()
        return most_popular_movie
    
    def default_bio(self):
        most_popular_movie = self.most_popular_movie()
        popular_movie_title = most_popular_movie.title if most_popular_movie else "No popular movie"
        
        # Generate bio string based on actor details
        bio = f"{self.name} is an actor"

        if self.birth_date != date(2000, 1, 1):
            birth_date_formatted = self.birth_date.strftime('%B %d, %Y')  # Format date to "Month Day, Year"
            bio += f" born on {birth_date_formatted}, they are currently {self.get_age()} years old."

        if self.birth_place != 'Not specified':
            bio += f" from {self.birth_place}"
        
        # Add nationality if specified
        if self.nationality != "Not specified":
            bio += f" They are of {self.nationality} nationality."
        
        # Add popular movie details
        if most_popular_movie:
            bio += f" best known for their work in movies such as {popular_movie_title}."
        
        return bio

    @staticmethod
    def ranked_actors():
        return Actor.objects.annotate(avg_rating=Avg('movies__reviews__rating')).order_by('-avg_rating')

    def get_rank(self): # update later and add followers so rankings can be more objective and reduce number of ties
        ranked_actors = Actor.ranked_actors().annotate(rank=Window(expression=Rank(), order_by=F('avg_rating').desc()))
        for actor in ranked_actors:
            if actor.pk == self.pk:
                return actor.rank
        return None
    
    def follower_count(self):
        from users.models import Follow
        actor_content_type = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=actor_content_type, object_id=self.pk).count()

class Director(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Non-Binary'),
    ]

    name = models.CharField(max_length=50)
    bio = models.TextField(default="No bio yet.")
    image = models.ImageField(upload_to="media", default="media/default.jfif")
    movies = models.ManyToManyField(Movie, related_name="directors")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="Not specified")
    birth_place = models.CharField(max_length=100, default="Not specified")
    nationality = models.CharField(max_length=50, default="Not specified")
    birth_date = models.DateField(default='2000-01-01')
    height = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def get_age(self):
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def avg_movie_rating(self):
        avg_rating = self.movies.aggregate(average=Avg('reviews__rating'))['average']
        return avg_rating or 0
    
    def most_popular_movie(self):
        most_popular_movie = self.movies.annotate(review_count=Count('reviews')).order_by('-review_count').first()
        return most_popular_movie
    
    def default_bio(self):
        most_popular_movie = self.most_popular_movie()
        popular_movie_title = most_popular_movie.title if most_popular_movie else "No popular movie"
        
        # Generate bio string based on actor details
        bio = f"{self.name} is an director"

        if self.birth_date != date(2000, 1, 1):
            birth_date_formatted = self.birth_date.strftime('%B %d, %Y')  # Format date to "Month Day, Year"
            bio += f" born on {birth_date_formatted}, they are currently {self.get_age()} years old."

        if self.birth_place != 'Not specified':
            bio += f" from {self.birth_place}"
        
        # Add nationality if specified
        if self.nationality != "Not specified":
            bio += f" They are of {self.nationality} nationality."
        
        # Add popular movie details
        if most_popular_movie:
            bio += f" best known for their work in movies such as {popular_movie_title}."
        
        return bio

    @staticmethod
    def ranked_directors():
        return Director.objects.annotate(avg_rating=Avg('movies__reviews__rating')).order_by('-avg_rating')

    def get_rank(self): 
        ranked_directors = Director.ranked_directors().annotate(rank=Window(expression=Rank(), order_by=F('avg_rating').desc()))
        for director in ranked_directors:
            if director.pk == self.pk:
                return director.rank
        return None
    
    def follower_count(self):
        from users.models import Follow
        director_content_type = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=director_content_type, object_id=self.pk).count()
    
class Award(models.Model):
    BEST_PICTURE = 'Best Picture'
    BEST_DIRECTOR = 'Best Director'
    BEST_ACTOR = 'Best Actor'
    BEST_ACTRESS = 'Best Actress'
    BEST_SUPPORTING_ACTOR = 'Best Supporting Actor'
    BEST_SUPPORTING_ACTRESS = 'Best Supporting Actress'
    BEST_CINEMATOGRAPHY = 'Best Cinematography'
    BEST_FILM_EDITING = 'Best Film Editing'
    BEST_PRODUCTION_DESIGN = 'Best Production Design'
    BEST_COSTUME_DESIGN = 'Best Costume Design'
    BEST_MAKEUP_HAIRSTYLING = 'Best Makeup and Hairstyling'
    BEST_VISUAL_EFFECTS = 'Best Visual Effects'
    BEST_ORIGINAL_SCORE = 'Best Original Score'
    BEST_SOUND = 'Best Sound'
    BEST_ANIMATED_FEATURE = 'Best Animated Feature'

    CATEGORY_CHOICES = [
        (BEST_PICTURE, 'Best Picture'),
        (BEST_DIRECTOR, 'Best Director'),
        (BEST_ACTOR, 'Best Actor'),
        (BEST_ACTRESS, 'Best Actress'),
        (BEST_SUPPORTING_ACTOR, 'Best Supporting Actor'),
        (BEST_SUPPORTING_ACTRESS, 'Best Supporting Actress'),
        (BEST_CINEMATOGRAPHY, 'Best Cinematography'),
        (BEST_FILM_EDITING, 'Best Film Editing'),
        (BEST_PRODUCTION_DESIGN, 'Best Production Design'),
        (BEST_COSTUME_DESIGN, 'Best Costume Design'),
        (BEST_MAKEUP_HAIRSTYLING, 'Best Makeup and Hairstyling'),
        (BEST_VISUAL_EFFECTS, 'Best Visual Effects'),
        (BEST_ORIGINAL_SCORE, 'Best Original Score'),
        (BEST_SOUND, 'Best Sound'),
        (BEST_ANIMATED_FEATURE, 'Best Animated Feature'),
    ]

    ACADEMY_AWARD = 'Academy Award'
    BAFTA = 'BAFTA'
    EMMY_AWARD = 'Emmy Award'
    GOLDEN_GLOBE = 'Golden Globe'

    AWARD_NAME_CHOICES = [
        (ACADEMY_AWARD, 'Academy Award'),
        (GOLDEN_GLOBE, 'Golden Globe'),
        (BAFTA, 'BAFTA'),
        (EMMY_AWARD, 'Emmy Award'),
    ]

    award_name = models.CharField(max_length=50, choices=AWARD_NAME_CHOICES, default=ACADEMY_AWARD)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='awards')  # Required field
    actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True, related_name='awards')  
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, blank=True, related_name='awards')  
    winner = models.BooleanField(default=True) # winner by default, nominated only if false
    year = models.PositiveIntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=BEST_PICTURE)

    def recipient(self):
        if self.actor:
            recipient = self.actor.name
        elif self.director:
            recipient = self.director.name
        elif self.movie:
            recipient = self.movie.title
        return recipient

    def __str__(self):
        recipient = self.recipient()

        status = "Winner" if self.winner else "Nominee"
        return f"{self.award_name} for {self.category} - {recipient} ({self.year}) [{status}]"