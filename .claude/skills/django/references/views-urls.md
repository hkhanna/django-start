# Views and URLs

## Views

- Keep the view thin: read and validate input, call a model method or a service, return a response. Domain logic belongs on the model layer (see `models.md`).
- Write every view as a function, including standard create, list, detail, update, and delete work. Class-based views are out, generic ones included; when several views share a flow, factor the shared piece into a plain helper function.
- Enforce access at the view boundary with `login_required` and the permission decorators, so an unauthorized request is turned away before it reaches the logic.
- Use querysets defined on the model's manager rather than assembling filters inline in the view.

## URLs

- Give every route a `name`, and set an `app_name` namespace per app. Refer to routes by `{namespace}:{name}` throughout the code and templates.
- Define routes with `path()`.
