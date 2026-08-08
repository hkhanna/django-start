# Form rendering

Validation rules live in the django skill's `forms.md`; this file covers how a form reaches the browser.

- Keep the form's markup in one shared `_form.html` partial rendered by every page that shows the form: `{% include "app/_form.html" with form=form only %}`. Render `form.non_field_errors` prominently at the top and each field's `errors` beside its field — domain errors the view adds with `form.add_error(None, …)` land in the non-field slot, so the template must render it.
- Inside `_form.html`, loop the fields (`{% for field in form %}`): label via `{{ field.label_tag }}`, the widget with Tailwind classes applied via django-widget-tweaks — `{{ field|add_class:"…" }}` — then `field.errors` and `field.help_text`. Branch on `{{ field|widget_type }}` where a widget needs different wrapping (selects, checkboxes). One loop styles every form in the project; `uv add django-widget-tweaks` the first time.
- Submit with htmx: the `<form>` carries `hx-post` (plus `method="POST" action=""` so the non-JS path works) and re-renders its own partial. On validation failure the view responds `status=422` (swap config in `htmx.md`); on success it redirects with `HX-Redirect` or fires an `HX-Trigger` event for the page to react to.
- Feedback before submit comes from the browser, not the server: emit `required`, `pattern`, `min`/`max` through field arguments and `Widget.attrs`, and pick the input type at the widget (`DateInput(attrs={"type": "date"})`). Server-side errors arrive on submit.
- `Widget.attrs` carries semantic attributes (type, autocomplete, placeholder); styling stays in `_form.html` with the rest of the Tailwind classes.
