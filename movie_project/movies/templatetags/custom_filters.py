from django import template

from movies.models import Actor, Director

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