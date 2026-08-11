from django import forms
from django.template import Context, Template


class ExampleForm(forms.Form):
    plain = forms.CharField()
    styled = forms.CharField(widget=forms.TextInput(attrs={"class": "existing"}))


def render_field(field_expr: str) -> str:
    template = Template("{% load add_class %}" + field_expr)
    return template.render(Context({"form": ExampleForm()}))


def test_add_class_applies_classes():
    """The filter puts the given classes on the rendered widget."""
    html = render_field('{{ form.plain|add_class:"border rounded" }}')
    assert 'class="border rounded"' in html


def test_add_class_merges_with_widget_classes():
    """Classes declared in Widget.attrs must survive the filter, not be replaced."""
    html = render_field('{{ form.styled|add_class:"border" }}')
    assert 'class="existing border"' in html
