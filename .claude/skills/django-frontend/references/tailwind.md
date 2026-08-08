# Tailwind

- The toolchain is project-specific: find how the project builds Tailwind (a Tailwind config or CSS entry point, `django-tailwind-cli` in `pyproject.toml`, a `package.json` script) and use its build and watch commands rather than introducing new tooling.
- Style with utilities directly in the template. The unit of reuse is the component — a shared `_partial.html` or inclusion tag carrying its markup and classes — not a custom CSS class; the stylesheet stays close to Tailwind's defaults.
- Write complete class names. Tailwind's scanner only sees literal strings, so choose between full names in template branches (`{% if urgent %}bg-red-100{% else %}bg-gray-100{% endif %}`); a name assembled from fragments (`bg-{{ color }}-100`) silently generates nothing.
- Templates in a new location must be visible to Tailwind's source scanning (content globs, or v4 source detection). A class that mysteriously doesn't apply usually means the file isn't scanned.
- Take design values (colors, spacing, fonts) from the project's Tailwind theme, and extend the theme for a value the design reuses; arbitrary one-off values (`mt-[13px]`) stay rare.
