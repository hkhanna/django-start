# Adding dependencies

Reach for the standard library and Django's built-ins first. When a third-party package is the right call, confirm it clears each bar before adding it:

- **Maintained** — recent commits and releases, and issues being handled.
- **Compatible** — supports the Python and Django versions in `pyproject.toml`.
- **Licensed** — a license that fits the project's use.
- **Worth its surface** — it saves enough work to justify one more dependency to track and upgrade, weighed against writing the small piece yourself.

Add it with `uv add` so it is pinned in `uv.lock`, and record why a non-obvious choice was made in the commit message.
