from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter("iconbool", is_safe=True)
def iconbool(value):
    """Given a boolean value, this filter outputs a font-awesome icon + the
    word "Yes" or "No"

    Example Usage:

        {{ user.has_widget|iconbool }}

    """
    if bool(value):
        result = '<i style="color: green" class="fa fa-check-circle"></i>'
    else:
        result = '<i style="color: red" class="fa fa-times-circle"></i>'
    return mark_safe(result)
