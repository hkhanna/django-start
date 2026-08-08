# HTMX

The server renders HTML: an htmx request gets back a fragment ready to swap in, and the server owns the state. HTMX is glue, not a client-side framework.

## The partial pattern

One pattern covers fragment rendering: the template wraps each swappable region in a `{% partialdef %}`, names that partial in the request with `hx-vals`, and the view opts in with `@for_htmx`. The complete routing — what swaps, into what, rendered from which partial — is readable in the template; the view never learns which fragments exist.

```html+django
{% partialdef item-list inline %}
  <div id="item-list"
    hx-get=""
    hx-vals='{"use_partial": "item-list"}'
    hx-target="#item-list"
    hx-swap="outerHTML">
    {% for item in items %}…{% endfor %}
  </div>
{% endpartialdef %}
```

```python
@for_htmx
def item_list(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "app/list.html", {"items": ...})
```

`inline` renders the partial in place on the full page; for an htmx request naming it, the decorator narrows the response to `"app/list.html#item-list"`. The decorator and its helpers are house utilities in a `core/htmx.py` — reuse the project's copy if one exists, otherwise add:

```python
import copy
from functools import wraps

from django.http import HttpRequest, HttpResponse, QueryDict
from django.template.loader import render_to_string
from django.utils.cache import patch_vary_headers


def is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def for_htmx(view):
    """For an htmx request naming use_partial, render only those partials."""

    @wraps(view)
    def _view(request, *args, **kwargs):
        resp = view(request, *args, **kwargs)
        if not is_htmx(request) or not hasattr(resp, "render"):
            return resp
        partials = request.GET.getlist("use_partial") or request.POST.getlist("use_partial")
        if not partials:
            return resp
        if len(partials) == 1:
            resp.template_name = f"{resp.template_name}#{partials[0]}"
        else:
            # Several partials at once (out-of-band swaps): render each and concatenate.
            resp = HttpResponse(
                "".join(
                    render_to_string(f"{resp.template_name}#{name}", resp.context_data, request)
                    for name in partials
                ),
                status=resp.status_code,
                headers=resp.headers,
            )
        # Fragment and full page share a URL, so HTTP caches must key on the header.
        patch_vary_headers(resp, ("HX-Request",))
        return resp

    return _view


def make_get_request(request: HttpRequest) -> HttpRequest:
    """Internal-redirect helper: the same request, re-shaped as a GET."""
    new_request = copy.copy(request)
    new_request.POST = QueryDict()
    new_request.method = "GET"
    return new_request
```

- The client names the partial, so treat `use_partial` as user input: permission checks live in the view, or inside the partial itself. An `{% if perm %}` wrapped *around* a partialdef is bypassed by requesting the partial directly.
- Keep the non-JS path working where it costs one attribute: a form carries `method="POST" action=""` alongside `hx-post`, a pager link a real `href` alongside `hx-get`. Non-htmx requests already get the full page, and tests can exercise the view without a browser.

## POSTs in a single view

A page's actions post back to the page's own view rather than to per-action endpoints. Buttons carry `name` attributes and the view branches on which name arrived in the POST data:

```python
@for_htmx
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Item.objects.all(), id=item_id)
    if request.method == "POST":
        if "archive" in request.POST:
            item.archive()
        elif "restore" in request.POST:
            item.restore()
        if not is_htmx(request):
            return HttpResponseRedirect("")
    return TemplateResponse(request, "app/item_detail.html", {"item": item})
```

- A plain request keeps POST/redirect/GET; an htmx POST falls through and renders the requested partial directly — the redirect round-trip is unnecessary when no full page reloads.
- The fragment is hypermedia: the template renders only the actions valid in the current state (`{% if item.is_archived %}` shows the restore button, otherwise archive), so the swap itself updates what the user can do next. Available actions are a server-side decision, rendered per state — never two buttons with a client-side toggle.
- **View restart.** Falling through renders with whatever the view computed *before* the mutation. When the view derives data up front (partitioned lists, aggregates), re-enter it instead of patching locals: split the body into an inner function and, for an htmx POST, recurse with `make_get_request(request)` — an internal redirect that recomputes everything from the new state.

## Requests

- Send the CSRF token once from the body tag: `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>`. A form that also submits as a plain POST keeps its `{% csrf_token %}`.
- Give every trigger with noticeable latency `hx-disabled-elt="this"` and an `hx-indicator`, so a slow response reads as working rather than broken and can't be double-submitted.
- Idioms that earn their keep: `hx-swap="outerHTML"` to replace the target itself rather than its contents, `hx-trigger="keyup changed delay:300ms"` for debounced search, `hx-push-url="true"` for navigation-like swaps, `hx-confirm` for a confirmation prompt (a modal is for real content — see `modals.md`).
- Defer an expensive region (a slow count, an aggregate) to its own request: render it as an element with `hx-get` + `hx-vals` naming its partial and `hx-trigger="load"` — or `hx-trigger="revealed"` to wait until it scrolls into view. A spinner placed inside the element with class `htmx-indicator` shows during the request, no `hx-indicator` attribute needed.

## Responses

- On validation failure, re-render the form partial with `status=422`, and let it swap with a one-time config in `base.html` — by default htmx leaves 4xx responses unrendered and the error partial never appears:

  ```html
  <meta name="htmx-config"
    content='{"responseHandling":[{"code":"204","swap":false},{"code":"[23]..","swap":true},{"code":"422","swap":true},{"code":"[45]..","swap":false,"error":true}]}'>
  ```
- Return `204` when the action succeeded and nothing on the page needs to change; htmx swaps nothing on an empty success.
- Removing an element (an inline row delete) is an empty `200` — the empty body swaps the target away — or `hx-swap="delete"`. A `204` suppresses the swap, so the element would stay.
- Reach for response headers when the answer is more than a fragment: `HX-Trigger` fires a client-side event other elements listen for, `HX-Redirect` navigates after success, `HX-Retarget` and `HX-Reswap` override the requesting element's target and swap style, and `HX-Refresh` forces a full reload when a selective swap isn't worth it. A bare `HttpResponse` carrying only such headers passes through `@for_htmx` untouched.
- Name `HX-Trigger` events kebab-case (`{"item-created": item.id}`): HTML attributes are case-insensitive, so a camelCase event can never be heard by an Alpine `@item-created.window` listener. An htmx element listens with `hx-trigger="item-created from:body"`.

## Queries

- A partial renders once per row: when a list partial renders a hundred row partials each reading `item.label`, the queryset the view resolves must pre-join whatever the rows touch, or the page runs a hundred extra queries.
