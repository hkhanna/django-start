---
name: django
description: Django house standard for this codebase. Use when creating a Django project or app; writing or changing models, managers, views, forms, URLs, or settings; writing migrations; or adding a dependency. Encodes fat models / thin views and 12-factor config
---

# Django house standard

Two leading words carry most of this standard. Think with them by name whenever you write Django code.

**Fat models, thin views.** Domain logic lives on the model layer: a model method for one instance's behavior, a custom `QuerySet` (exposed as the model's manager) for reusable queries, and a plain service function — coordinating those models' own methods — when the logic spans several models. A view accepts a request, calls into that layer, and returns a response. As soon as domain logic starts collecting in a view, move it down to a model method or a service.

**12-factor.** Every value that differs between environments is read from the environment at runtime. Code carries a default only for local development.

## Stack and workflow

- Dependencies go through **uv**: `uv add <pkg>` for runtime, `uv add --group dev <pkg>` for tooling. Both update `pyproject.toml` and pin `uv.lock`. Commit `uv.lock` and treat it as authoritative; install with `uv sync`.
- Read the Python and Django versions from `pyproject.toml` before writing anything version-sensitive, and use APIs those versions provide.
- Work test-first: every change to production code starts from a failing test. The red-green-refactor loop and the testing standard live in the django-testing skill.

## Layout

- Settings live in a settings package split by environment, selected with `DJANGO_SETTINGS_MODULE`.
- Each app is a small, single-purpose package; a model count creeping past roughly ten is the signal to split it.
- Templates and static files live inside each app, namespaced by the app's name (`core/templates/core/…`, `core/static/core/…`). Settings discover them through `APP_DIRS` and the app-directories static finder 

## Reach for the reference that covers what you are touching

Pull in the matching file before you write. Each one holds the rules that change how this codebase wants the work done.

- Models, managers, or QuerySets → `references/models.md`
- Migrations → `references/migrations.md`
- Any code that reads through the ORM → `references/queries.md`
- Views or URLs → `references/views-urls.md`
- Forms → `references/forms.md`
- Templates, HTMX, Tailwind, or Alpine — anything the browser renders → the django-frontend skill
- Settings, environment, or secrets → `references/config.md`
- Adding a dependency → `references/packages.md`
- Finishing a change that touches auth, permissions, user input, or settings → `references/security-checklist.md`


