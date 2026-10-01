.PHONY: app css watch check all clean build mypy ruff djlint format db clear-db migrate seed

SHELL := /bin/bash
OP = op run --env-file=env.op --
DB_NAME = $(shell basename $(CURDIR))-db

# RUNNING AND TESTING #
app:
	$(OP) uv run python manage.py tailwind runserver

css:
	uv run python manage.py tailwind build

watch:
	uv run python manage.py tailwind watch

check: mypy ruff djlint
	uv run py.test

mypy:
	uv run mypy .

ruff:
	uv run ruff check
	uv run ruff format --check

djlint:
	uv run djlint . --lint --check

format:
	uv run ruff format
	uv run djlint . --reformat

# BUILD STEPS #
all: clean build db

clean:
	@echo "Removing python virtual environment"
	rm -rf .venv

build:
	@echo "Building python virtual environment"
	uv sync

db: clear-db migrate seed

clear-db:
# Make sure this is running on local
	@uv run python manage.py shell -v 0 -c "from django.conf import settings; import sys; sys.exit(0 if settings.DJANGO_ENV == 'local' else 1)"
	@read -p "Proceed to destroy database? (y/N): " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f db.sqlite3; \
		echo "Destroyed"; \
	else \
		echo "Operation cancelled."; \
		exit 1; \
	fi

migrate:
	@echo "Running migrations"
	uv run python manage.py migrate

seed: 
	@echo "Seeding database"
	uv run python manage.py seed_db


