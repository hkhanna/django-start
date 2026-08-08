# Templates

- Keep templates presentation-only. Compute values in the view or on the model and pass them through the context; the template reads the context and renders it.
- Two tiers of inheritance cover most sites: `base.html` holds the page shell, and each page extends it. Keep a small set of well-named blocks — `title`, `content`, `extra_head`, `extra_js` — rather than many granular ones.
- `base.html` loads htmx and Alpine as deferred `<script>` tags from static files (version in the filename), links the Tailwind build's stylesheet, and renders the messages framework once so flash feedback appears on every page.
- A fragment that htmx swaps and that belongs to one page is a `{% partialdef %}` inside that page's template (see `htmx.md`). A fragment shared across pages is a separate file named with a leading underscore (`_row.html`, `_form.html`), with `extends` left out.
- Include a shared partial with `{% include "app/_row.html" with row=row only %}`. The `only` keyword isolates the context, so the `with` clause documents exactly what the partial needs.
- Put an `{% empty %}` clause on any loop over user-visible data, so an empty list renders as a message rather than a blank region.
- Factor reusable display logic into template tags and filters. A tag or filter evaluated inside a loop must never query — it runs once per row of a list view; fetch that data in the view and pass it through the context. An inclusion tag rendered once per page (a header or footer component in `base.html`) may load its own data, so a shared component doesn't require touching every view's context.
- Data needed on nearly every page belongs in a context processor. Data shared by a group of pages comes from a plain helper function merged into each view's context (the django skill's `views-urls.md` covers the pattern).
- Rely on Django's automatic escaping. Sanitize any value before rendering it through `|safe` or `mark_safe`.
