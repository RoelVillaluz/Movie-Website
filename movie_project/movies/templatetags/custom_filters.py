from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary by key."""
    return dictionary.get(key)