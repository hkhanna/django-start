# Forms

- Validate incoming request data in a `Form` or `ModelForm`. This is the boundary where user input becomes trusted data. Put single-field checks in `clean_<field>()` and cross-field checks in `clean()`.
- Start a cross-field `clean()` with `cleaned = super().clean()`, so field-level validation runs first and keeps its errors.
- Act on `form.cleaned_data` after validation, so values reach the rest of the code already checked and coerced.
- A form checks the shape of input: presence, type, length, format, consistency between its own fields. A domain rule belongs on the model layer; the view calls it, catches the exception it raises, and surfaces the message with `form.add_error(None, str(exc))` before re-rendering.
- Rendering — how the form, its widgets, and its errors reach the browser — lives in the django-frontend skill.
