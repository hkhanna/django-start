# Templates

- Keep templates presentation-only. Compute values in the view or on the model and pass them through the context; the template reads the context and renders it.
- Two tiers of inheritance cover most sites: `base.html` holds the page shell, and each page extends it. Keep a small set of well-named blocks — `title`, `content`, `extra_head`, `extra_js` — rather than many granular ones.
- Name a partial with a leading underscore (`_row.html`, `_form.html`) and leave `extends` out of it; full pages extend `base.html`.
- Include a partial with `{% include "app/_row.html" with row=row only %}`. The `only` keyword isolates the context, so the `with` clause documents exactly what the partial needs.
- Put an `{% empty %}` clause on any loop over user-visible data, so an empty list renders as a message rather than a blank region.
- Render the messages framework once in `base.html`, so flash feedback appears on every page.
- Factor reusable display logic into template tags and filters, and keep them off the database — a tag or filter that queries runs once per row of a list view. Fetch the data in the view and pass it through the context.
- Rely on Django's automatic escaping. Sanitize any value before rendering it through `|safe` or `mark_safe`.
