from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    return value.replace(arg[0], arg[1])

