# Migrations

- Generate with `makemigrations`, then read the generated file before committing: confirm it makes the change you intended and that its operations reverse cleanly.
- Name migrations for what they do: `makemigrations <app> --name add_invoice_status`.
- Put a data migration in its own file, separate from schema changes, and give it a reverse function (`RunPython` with both directions — `migrations.RunPython.noop` when reversing the schema already undoes the data step). Inside it, obtain each model with `apps.get_model("app", "Model")`: the migration must run against the historical model state, which a direct import would bypass. A historical model carries fields only — custom methods and overridden `save()` don't exist on it — so do the work through field assignment and queryset operations.
- On a large table, stage a change that would otherwise hold a long lock: add a nullable column, backfill in batches, then add the constraint in a later migration.
- On deploy, migrations run in the start command (`render.yaml`), because the persistent disk holding the database is not mounted during build or pre-deploy. Read any migration that another change generated before it lands.
