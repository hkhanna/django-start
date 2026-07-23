# Views and URLs

## The pattern

Every HTML view starts from this shape — a type-hinted function returning a `TemplateResponse`:

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    return TemplateResponse(request, "shop/product_detail.html", {
        "product": get_object_or_404(Product.objects.all(), slug=slug),
    })
```

- Return `TemplateResponse` rather than `render`: it remembers its template and context, so tests can assert on them and decorators or middleware can inspect or adjust the response before it renders.
- Type-hint the signature; each URL parameter's type matches its path converter in `urls.py`.

## Views

- Keep the view thin: read and validate input, call a model method or a service, return a response. Domain logic belongs on the model layer (see `models.md`).
- Write every view as a function, including standard create, list, detail, update, and delete work. Class-based views are out, generic ones included. One exception: a route that does nothing but redirect may use `RedirectView.as_view(...)` directly in `urls.py`; the moment it needs any other logic, write it as a function.
- Enforce access at the view boundary with `login_required` and the permission decorators, so an unauthorized request is turned away before it reaches the logic.
- Use querysets defined on the model's manager rather than assembling filters inline in the view.
- Look up a single object with `get_object_or_404(Product.objects.all(), slug=slug)` — pass a queryset, never the bare model class, so narrowing it later (say, to `Product.objects.visible()`) is a one-place edit.
- Query user-owned data starting from the user object — `request.user.bookings.in_basket()`, not `Booking.objects.filter(...)` plus an ownership check — so ownership scoping is structural and an ID swapped into a URL can't reach another user's rows.

## Sharing logic between views

Compose with plain functions, escalating as the overlap grows:

- Shared context data → a function that returns a dict, merged into each view's context: `context = {...} | checkout_pages_context(request.user)`. (Data needed site-wide or by a template-level component is handled at the template layer — see `templates.md`.)
- Shared flow → the entry-point views delegate to one parameterized function taking the pieces that vary: queryset, template name, extra context.
- Shared flow with a varying step in the middle → pass a function as that parameter; a closure defined inside the entry-point view adapts a mismatched signature and carries the view's locals with it.

## URLs

- Give every route a `name`, and set an `app_name` namespace per app. Refer to routes by `{namespace}:{name}` throughout the code and templates.
- Define routes with `path()`.
