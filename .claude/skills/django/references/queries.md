# ORM queries

- Load related data in the query itself: `select_related` for forward `ForeignKey` and one-to-one, `prefetch_related` for reverse relations and many-to-many. When a prefetch needs its own filtering or `select_related`, pass a `Prefetch` object.
- Resolve queries where the whole access pattern is visible (the view or the service) and pass the results into the template through the context. Query logic stays out of templates.
- For counts, existence, and aggregates, use `.count()`, `.exists()`, and `.aggregate()` rather than loading rows into Python to measure them.
- Act on many rows in a single statement with `bulk_create`, `bulk_update`, or a queryset `.update()`.
- Update a value in place with an `F()` expression (`.update(views=F("views") + 1)`), so the arithmetic runs in the database as one atomic statement rather than a read-modify-write in Python.
- When a page's query count grows as the data grows, add the missing `select_related` or `prefetch_related`, or move the access onto a manager method. A query sitting inside a loop is the usual cause.
