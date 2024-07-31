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

    def __str__(self):
        return self.title