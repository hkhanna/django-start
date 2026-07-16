---
name: django-testing
description: Testing standard for this Django codebase, using pytest and pytest-django. Use when writing, changing, or fixing tests, adding test coverage, or setting up test fixtures and factories.
---

# Testing standard

Tests run under **pytest** with **pytest-django**. Name test files to match `test*.py` (pytest's `python_files` setting) — an app's `tests.py`, or `test_models.py` when tests split by module — and test functions `test_*`. Follow arrange, act, assert: set up the data, take the action, assert on the outcome.

## Red, green, refactor

Work test-first. Write a failing test that describes the behavior you want (red), write the minimum code that makes it pass (green), then clean up with the tests still green (refactor). Every change to production code starts from a failing test that demands it.

## Configuration

- Run tests against the dedicated test settings module (`config.settings.test`, selected in the pytest configuration), which swaps file storage to in-memory. Put any other test-only override there rather than in a fixture.

## Database access

- pytest-django gives a test no database by default. Mark a test that touches the ORM with `@pytest.mark.django_db`, and apply it file-wide with `pytestmark = pytest.mark.django_db` when most tests in a module need the database.

## Test data

- Create model instances through builder functions in a `factories.py` alongside the tests. Name each `make_<model>`, fill defaults with a module-level `Faker()` instance, accept `**overrides`, and apply them as `defaults | overrides` so a test pins only the fields it cares about. Default a foreign key by calling the related model's builder. These plain functions are the house pattern; factory_boy and model_bakery stay out. The `faker` package is not yet a dev dependency — `uv add --group dev faker` the first time a factory needs it; its pytest plugin also provides the `faker` and `faker_seed` fixtures.
- Inside a test body, generate one-off fake values with the `faker` fixture, and set the `faker_seed` fixture when a test needs reproducible values.
- Keep `conftest.py` fixtures for clients and shared mocks — an authenticated client, a stubbed external service. Data construction stays in the builders, where a per-test override is a keyword argument rather than a fixture indirection.

## What to test

- Cover your own logic: model methods, manager and QuerySet methods, services, form validation, and the responses your views return. Leave Django's own machinery to Django.
- Exercise a view through pytest-django's `client` fixture and assert on both the status and the effect; build a raw request with `rf` when a unit needs one.
- Test the denial path of any view that enforces auth or ownership: an anonymous request is redirected, and a request for another user's record gets a 403 or 404.
- Exercise both branches of an HTMX-aware view: pass `HTTP_HX_REQUEST="true"` through the client and assert the partial rendered, and hit it plain to assert the full page.
- Exercise a database constraint by writing the violating row and asserting it raises `IntegrityError`.
- Pin the query count of a hot view or reusable query with the `django_assert_num_queries` fixture, so an N+1 regression fails the suite.
- Mock at the boundary — the HTTP client, the email backend, the task queue — and let your own code run for real.
- Override configuration for a single test with the `settings` fixture rather than changing settings globally.
- Cover a range of inputs with `@pytest.mark.parametrize` rather than copying a test per case.

## Coverage

Aim coverage at the model layer and service functions, where the domain logic lives. Meaningful assertions there matter more than a high percentage spread across boilerplate.
