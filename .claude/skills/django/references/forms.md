# Forms

- Validate incoming request data in a `Form` or `ModelForm`. This is the boundary where user input becomes trusted data. Put single-field checks in `clean_<field>()` and cross-field checks in `clean()`.
- Start a cross-field `clean()` with `cleaned = super().clean()`, so field-level validation runs first and keeps its errors.
- List a `ModelForm`'s fields explicitly in `Meta.fields`. An explicit list keeps a field added to the model later from silently appearing in the form.
- Act on `form.cleaned_data` after validation, so values reach the rest of the code already checked and coerced.
- A form checks the shape of input: presence, type, length, format, consistency between its own fields. A domain rule belongs on the model layer; the view calls it, catches the exception it raises, and surfaces the message with `form.add_error(None, str(exc))` before re-rendering.
- Render `form.non_field_errors` prominently and each field's `errors` beside its field, and keep that markup in a `_form.html` partial shared by every page that shows the form. Domain errors surfaced in the view land in the non-field slot, so the template must render it.
