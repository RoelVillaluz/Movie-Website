from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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
    overview = models.TextField(max_length=255)
    poster_path = models.ImageField(upload_to="media")
    backdrop_path = models.ImageField(upload_to="media")
    release_date = models.DateField()
    genres = models.ManyToManyField('Genre', blank=True)

    def __str__(self):
        return self.title
    
class Genre(models.Model):
    ACTION = 'Action'
    COMEDY = 'Comedy'
    DRAMA = 'Drama'
    HORROR = 'Horror'
    ROMANCE = 'Romance'
    SCIFI = 'Sci-Fi'
    THRILLER = 'Thriller'
    ANIMATION = 'Animation'
    MARVEL = 'Marvel'
    DC = 'DC'
    FANTASY = 'Fantasy'
    MYSTERY = 'Mystery'
    CRIME = 'Crime'
    ADVENTURE = 'Adventure'
    DOCUMENTARY = 'Documentary'
    FAMILY = 'Family'
    MUSICAL = 'Musical'
    WESTERN = 'Western'
    WAR = 'War'
    HISTORY = 'History'
    BIOGRAPHY = 'Biography'
    SPORT = 'Sport'
    MUSIC = 'Music'
    SHORT = 'Short'
    INDIE = 'Indie'
    NOIR = 'Noir'
    SUPERHERO = 'Superhero'

    GENRE_CHOICES = [
        (ACTION, 'Action'),
        (COMEDY, 'Comedy'),
        (DRAMA, 'Drama'),
        (HORROR, 'Horror'),
        (ROMANCE, 'Romance'),
        (SCIFI, 'Sci-Fi'),
        (THRILLER, 'Thriller'),
        (ANIMATION, 'Animation'),
        (MARVEL, 'Marvel'),
        (DC, 'DC'),
        (FANTASY, 'Fantasy'),
        (MYSTERY, 'Mystery'),
        (CRIME, 'Crime'),
        (ADVENTURE, 'Adventure'),
        (DOCUMENTARY, 'Documentary'),
        (FAMILY, 'Family'),
        (MUSICAL, 'Musical'),
        (WESTERN, 'Western'),
        (WAR, 'War'),
        (HISTORY, 'History'),
        (BIOGRAPHY, 'Biography'),
        (SPORT, 'Sport'),
        (MUSIC, 'Music'),
        (SHORT, 'Short'),
        (INDIE, 'Indie'),
        (NOIR, 'Noir'),
        (SUPERHERO, 'Superhero'),
    ]

    name = models.CharField(max_length=24, choices=GENRE_CHOICES)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])

    def __str__(self):
        return f"{self.user}'s Review for {self.movie}: {self.rating} stars"
