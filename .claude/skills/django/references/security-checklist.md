# Security checklist

Before finishing a change that touches authentication, permissions, user input, or settings, confirm every item that applies:

- Every view exposing non-public data enforces authentication and the right authorization.
- Request data reaches the database only after passing through a form or another validated path.
- Secrets are read from the environment; none are hardcoded, and none are written to logs.
- `DEBUG` is driven by the environment and stays off outside local development.
- Records and querysets are scoped to the requesting user wherever ownership matters, so changing an ID in a URL lands only on data that user may see.
- User-supplied content renders through Django's escaping, and any value marked safe has been sanitized first.
