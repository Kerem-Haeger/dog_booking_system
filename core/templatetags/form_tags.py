from django import template
from django.forms import BoundField
from django.forms.widgets import Widget

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Add CSS class to a form field widget
    Usage: {{ form.field|add_class:"my-class" }}
    """
    if not css_class:
        return field

    # Handle BoundField (form fields in templates)
    if isinstance(field, BoundField):
        widget = field.field.widget
        if hasattr(widget, 'attrs'):
            existing_classes = widget.attrs.get('class', '')
            if existing_classes:
                widget.attrs['class'] = f"{existing_classes} {css_class}"
            else:
                widget.attrs['class'] = css_class

    # Handle direct widget access
    elif hasattr(field, 'widget') and isinstance(field.widget, Widget):
        existing_classes = field.widget.attrs.get('class', '')
        if existing_classes:
            field.widget.attrs['class'] = f"{existing_classes} {css_class}"
        else:
            field.widget.attrs['class'] = css_class

    return field
