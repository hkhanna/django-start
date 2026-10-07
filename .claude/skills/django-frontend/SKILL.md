---
name: django-frontend
description: Frontend standard for this Django stack — server-rendered templates, Tailwind, HTMX, Alpine. Use when writing or changing templates or partials, adding HTMX interactions or HTMX-aware views, styling with Tailwind, writing client-side behavior with Alpine, rendering forms, or building modals.
---

# Django frontend standard

The stack is Django templates + Tailwind + HTMX + Alpine, on Django ≥ 6.0 (the partial pattern depends on built-in template partials). Four leading ideas carry the standard; think with them by name.

**The server owns the HTML.** Every interaction that reads or writes data is a request that returns server-rendered hypermedia — a full page, or a fragment htmx swaps in — carrying both the new state and the actions now available from it. State lives in the database; pages get no JSON endpoints, no client-side rendering, no client-side model.

**htmx is earned.** The default interaction is a plain request: a form posts and redirects, a link navigates, a validation failure re-renders the full page. An interaction earns `hx-` attributes through one of four payoffs — **latency** (a slow request needs an in-flight indicator), **place** (an in-place swap keeps context a reload would lose: scroll position in a long list, state elsewhere on a busy page), **liveness** (the interaction reacts as the user acts: debounced search, a deferred expensive region), or **history** (a success that redirects back to the page the form sits on stacks a duplicate history entry, so Back stops leading where the user came from). A form whose success navigates elsewhere, on a page that is only the form, is a plain form.

**Alpine owns the client.** Behavior that never touches the server — open/closed state, an active tab, showing a dialog, reacting to an event — is Alpine's, written as `x-` attributes in the markup. Alpine never fetches; the moment data is involved, it's an htmx request.

**Locality of behaviour.** Everything a region of the page does should be readable in that region's markup: its Tailwind classes, its `hx-` attributes, the partial it re-renders as, its Alpine state. Behavior is declared as attributes on the element it affects — abstract an implementation freely (`for_htmx`, an `Alpine.data()` component), but its invocation stays on the element. Reach for action-at-a-distance — a hoisted `hx-` attribute, a global listener — only when everything it reaches genuinely shares the behavior; the body-level CSRF header is the house example.

Validation logic, view structure, and model rules live in the django skill; this skill covers everything the browser renders.

## Reach for the reference that covers what you are touching

- Templates or partials → `references/templates.md`
- Whether an interaction earns htmx, any `hx-` attribute, fragment swap, or HTMX-aware view → `references/htmx.md`
- Client-side behavior → `references/alpine.md`
- Tailwind styling → `references/tailwind.md`
- Rendering a form → `references/forms.md`
- Modal dialogs → `references/modals.md` (builds on htmx.md and alpine.md)
