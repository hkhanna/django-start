from django import template
from django.forms import BoundField
from django.utils.safestring import SafeString

register = template.Library()


@register.filter
def add_class(field: BoundField, css: str) -> SafeString:
    """Render a bound field's widget with extra CSS classes appended."""
    # Attrs passed to as_widget replace same-key widget attrs, so merge by hand.
    attrs = field.field.widget.attrs
    merged = f"{attrs.get('class', '')} {css}".strip()
    return field.as_widget(attrs={"class": merged})
