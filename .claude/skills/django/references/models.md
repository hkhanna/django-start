# Models

## Where logic lives

- Behavior for one instance → a method on the model.
- A query you reuse → a method on a custom `QuerySet` subclass, exposed as the manager with `objects = MyQuerySet.as_manager()`. Callers then chain `Model.objects.active().recent()` instead of repeating the same filters at each call site. A query method narrows results when called; the manager never filters `get_queryset()`, so `Model.objects` reaches the full table.
- An alternate constructor → a manager method (`RGBColor.objects.from_hex("#000080")`), not a classmethod on the model.
- Logic that spans several models → a plain function in the app's `services.py`, called from the view. A service function coordinates by calling the models' public methods and managers; behavior belonging to one model stays on that model, however many steps it takes.
- A reaction to a domain event → an explicit call in the model method or service function that causes the event. A signal receiver is for reacting to a model you don't own — a third-party app or `django.contrib.auth` — never for your own models calling each other.

Outside the model layer, mutate an instance through its methods: a view or service function that sets fields and calls `save()` is a model method waiting to be named. Persisting a validated `ModelForm` with `form.save()` stays in the view.

## Required fields

Every non-proxy model in the project defines these three fields — the `core.E001` system check fails `manage.py check` without them:

```python
uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
created_at = models.DateTimeField(db_index=True, default=timezone.now)
updated_at = models.DateTimeField(auto_now=True)
```

## Model hygiene

- Set `related_name` explicitly on every `ForeignKey` and `ManyToManyField`.
- Set `null` and `blank` deliberately: `blank` controls form validation, `null` controls the database column. Django stores an empty value as `''` in text-backed fields (`CharField`, `TextField`, `SlugField`, `EmailField` — and `FileField`, which stores a path) and as `NULL` in every other column type. So an optional text field takes `blank=True` alone, and an optional field of any other type — numeric, date, boolean, `ForeignKey` — takes `blank=True, null=True`. The exception is a unique, optional text field, which needs `null=True` so multiple blank rows don't collide on the unique constraint. (`null` has no effect on `ManyToManyField`.)
- Define a choice field's options as an inner `TextChoices` or `IntegerChoices` class and reference them as `Model.Kind.VALUE`. Move the class out of the model only when several models share it.
- Store money and other exact quantities in a `DecimalField`. Store points in time as timezone-aware `DateTimeField`.
- Give each model a `__str__` built from its own fields — one that reads a related object runs a query per row in the admin and shell — and a `Meta.ordering` when the rows have a natural order.

## Inheritance

Share repeated fields through an abstract base model (`class Meta: abstract = True`); a field or two in common just gets declared on both models. Multi-table inheritance is out — subclassing a concrete model adds a hidden table and a join to every query — link the models with an explicit `OneToOneField` or `ForeignKey` instead.

## Integrity at the database

Enforce invariants with database constraints (`UniqueConstraint`, `CheckConstraint` in `Meta.constraints`) as well as in application code, so the guarantee holds even when a row is written from a migration, the shell, or another service.

Relate models with real `ForeignKey`, `OneToOneField`, and `ManyToManyField` fields. `GenericForeignKey` is out — the database cannot index or constrain the relation, so queries slow down and rows can point at deleted records.

## Enforcing conventions

Back a project-wide model convention with a Django system check registered in a `checks.py`, raising a project-namespaced error id. `manage.py check` and the test suite then fail the moment a model drifts, instead of the rule living only in review comments.
