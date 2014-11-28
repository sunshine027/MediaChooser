from django import template

register = template.Library()

@register.filter
def first_subpath(value):
    return value.split("/")[1]
    #return value
