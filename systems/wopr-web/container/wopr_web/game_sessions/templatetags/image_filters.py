from django import template

register = template.Library()


@register.filter
def strip_base_path(value):
    return value.replace("/remote/wopr", "")
