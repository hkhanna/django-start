# Configuration

## 12-factor config

- Every environment-dependent value is read from the environment under a `DJANGO_`-prefixed name: `DJANGO_SETTINGS_MODULE`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`. Provide a development default only where running locally would otherwise break, and never hardcode a real secret — `local.py` and `test.py` carry a throwaway insecure key; production reads `DJANGO_SECRET_KEY`.
- `DEBUG` defaults to off (`DJANGO_DEBUG` in `common.py`); `local.py` hardcodes it on for development.
- Production `ALLOWED_HOSTS` comes from `RENDER_EXTERNAL_HOSTNAME`, which Render sets automatically.

## Settings structure

- Settings live in `config/settings/`: shared defaults in `common.py`, plus one module per environment — `local.py`, `production.py`, `test.py` — selected by `DJANGO_SETTINGS_MODULE` (`manage.py` defaults to `config.settings.local`).
- An environment swaps a backing service by overriding it in its settings module, not through a connection-string variable: `production.py` moves the database and media onto the persistent disk and switches static files to WhiteNoise; `test.py` switches file storage to in-memory.

## State lives on the persistent disk

- Production is a single node with a Render persistent disk mounted at `/var/data` (`DISK_DIR`). The SQLite database and uploaded media live on that disk and survive deploys; sessions are database-backed. There is no separate database service or object storage — do not introduce `DATABASE_URL` or an S3 storage backend.
- Send logs to stdout and stderr as a stream and let the platform collect them, rather than opening and rotating log files inside the app.

## Dependencies and release

- Declare runtime dependencies and dev tooling as separate groups in `pyproject.toml`, and add them with `uv add` so `uv.lock` stays pinned.
- Migrations run in the deploy's start command (`render.yaml`), not at build or pre-deploy: the disk that holds the database is only mounted at runtime.
