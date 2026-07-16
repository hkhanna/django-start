# HTMX

- The server renders HTML: an HTMX request gets back a fragment ready to swap in, and the server owns the state. HTMX is glue, not a client-side framework.
- Keep one partial per swappable region. The full page includes the partial (`{% include "app/_list.html" with items=items only %}`), and the view returns that same partial standalone to an HTMX request — one template serves both paths.
- Branch on the request once, at the response boundary of the view: `request.headers.get("HX-Request")` chooses the partial or the full page. Code below the view stays HTMX-unaware.
- On validation failure, re-render the form partial with `status=422`. Pair this with a one-time `htmx.config.responseHandling` entry that lets 4xx responses swap — by default htmx leaves them unrendered, and the error partial never appears.
- Return `204` when the action succeeded and nothing on the page needs to change; htmx swaps nothing on an empty success.
- Reach for response headers when the answer is more than a fragment: `HX-Trigger` fires a client-side event other elements listen for (`hx-trigger="thread:created from:body"`), `HX-Redirect` navigates after success, `HX-Retarget` and `HX-Reswap` override the requesting element's target and swap style, and `HX-Refresh` forces a full reload when a selective swap isn't worth it.
- Give every trigger with noticeable latency `hx-disabled-elt="this"` and an `hx-indicator`, so a slow response reads as working rather than broken and can't be double-submitted.
- Send the CSRF token once from the body tag: `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>`. A form that also submits as a plain POST keeps its `{% csrf_token %}`.
- Idioms that earn their keep: `hx-swap="outerHTML"` to replace the target itself rather than its contents, `hx-trigger="keyup changed delay:300ms"` for debounced search, `hx-push-url="true"` for navigation-like swaps.
- A partial renders once per row: when `_list.html` includes a hundred `_row.html` each reading `thread.label`, the queryset the view resolves must pre-join whatever the partials touch, or the page runs a hundred extra queries.
