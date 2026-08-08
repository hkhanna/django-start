# Modals

Default to editing in place — the region swaps to its edit form and back with the partial pattern. A modal is for a flow that genuinely interrupts the page (creating a record without leaving the current context), and `hx-confirm` covers plain confirmation prompts.

A modal is a `<dialog>` loaded on demand: a button fetches the modal's HTML from its own view and appends it to the body, Alpine shows it, events close it.

The opening button, on the parent page:

```html+django
<button hx-get="{% url 'app:item_create' %}" hx-target="body" hx-swap="beforeend">
  Add an item
</button>
```

The modal template — a standalone `<dialog>` whose Alpine attributes are the entire modal machinery (show on load, remove from the DOM on close, close when the server says so; native `close` also fires on Esc and on `method="dialog"` buttons):

```html+django
<dialog x-data x-init="$el.showModal()" @close="$el.remove()" @close-modal.window="$el.close()"
        class="…">
  {% partialdef dialog-contents inline %}
    <form
      hx-post="{{ request.get_full_path }}"
      hx-vals='{"use_partial": "dialog-contents"}'
      hx-target="closest dialog"
      hx-swap="innerHTML"
    >
      {% include "app/_form.html" with form=form only %}
      <button type="submit">Save</button>
    </form>
    <form method="dialog"><button>Cancel</button></form>
  {% endpartialdef %}
</dialog>
```

`hx-post="{{ request.get_full_path }}"`, not a relative URL: the browser's address is still the parent page, so `hx-post=""` would post to the wrong view.

The view is a standard create-form view; success closes the modal and announces the new object:

```python
@for_htmx
def item_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return HttpResponse(
                headers={"HX-Trigger": json.dumps({"close-modal": True, "item-created": item.id})}
            )
        status = 422
    else:
        form = ItemForm()
        status = 200
    return TemplateResponse(request, "app/item_create_modal.html", {"form": form}, status=status)
```

- The opening GET names no partial, so the full `<dialog>` renders and lands at the end of the body; a POST names `dialog-contents`, so validation errors re-render inside the open dialog (422 swap config in `htmx.md`). The bare success response passes through `@for_htmx` untouched.
- The parent-page region that shows the new item refreshes itself by listening for the announced event, with the usual partial pattern:

```html+django
{% partialdef item-list inline %}
  <div id="item-list"
    hx-get=""
    hx-trigger="item-created from:body"
    hx-vals='{"use_partial": "item-list"}'
    hx-target="#item-list"
    hx-swap="outerHTML">
    …
  </div>
{% endpartialdef %}
```
