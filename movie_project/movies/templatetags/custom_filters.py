from django import template

from movies.models import Actor, Director, Movie
from users.models import Favorite
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary by key."""
    return dictionary.get(key)

@register.filter
def is_actor(person):
    return isinstance(person, Actor)
 
@register.filter
def is_director(person):
    return isinstance(person, Director)

@register.filter
def is_favorite(profile, movie):
    return Favorite.objects.filter(profile=profile, content_type=ContentType.objects.get_for_model(Movie), object_id=movie.id).exists()

@register.filter
def range_template(value):
    return range(value)